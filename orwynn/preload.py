"""
Manages preloaded files, i.e. files that need to be loaded before the main
instruction send.
"""
import asyncio
import shutil
from pathlib import Path
from typing import Any

import aiofiles
import aiohttp.web
from pydantic import BaseModel
from pykit.dt import DtUtils
from pykit.err import InpErr
from pykit.log import log
from pykit.query import SearchQuery, UpdQuery

from orwynn.cfg import Cfg
from orwynn.dto import Udto
from orwynn.mongo import Doc
from orwynn.sys import Sys


class PreloadUdto(Udto):
    filenames: list[str]
    createdTime: float
    expireTime: float

class PreloadDoc(Doc):
    filenames: list[str]
    createdTime: float
    expireTime: float


class UploadFile(BaseModel):
    filename: str
    # we use any type because of Windows-Linux unknown factors
    buf: Any
    content_type: str

    class Config:
        arbitrary_types_allowed = True


class PreloadCfg(Cfg):
    must_clean_preloads_on_destroy: bool = False


class PreloadSys(Sys[PreloadCfg]):
    # All preloaded files are stored in var/preload dir, under corresponding
    # dir with preload_sid name. Every stored file has it's original filename.

    _DefaultExpirationDelta = 3600.0 # = 1 hour

    async def init(self):
        self._BasePreloadDir = Path(
            Path.cwd(),
            "var/preload"
        )
        self._del_tasks: set[asyncio.Task] = set()

    async def preload(self, files: list[UploadFile]) -> PreloadUdto:
        if not files:
            raise InpErr("empty file list")

        preload = PreloadDoc(
            filenames=[],
            createdTime=DtUtils.get_utc_timestamp(),
            expireTime=DtUtils.get_delta_timestamp(
                self._DefaultExpirationDelta
            )
        ).create()

        del_task = asyncio.create_task(self._del_preload_on_expire(preload))
        self._del_tasks.add(del_task)
        del_task.add_done_callback(self._del_tasks.discard)

        preload_target_dir = Path(self._BasePreloadDir, preload.sid)
        preload_target_dir.mkdir(parents=True, exist_ok=True)

        for f in files:
            if not f.filename:
                raise InpErr("ufile with empty filename")

            preload.filenames.append(f.filename)
            save_path = Path(preload_target_dir, f.filename)
            async with aiofiles.open(save_path, "wb+") as out_file:
                content: bytes = f.buf.read()
                f.buf.close()
                await out_file.write(content)

        preload = preload.upd(UpdQuery.create(set={
            "filenames": preload.filenames
        }))

        return PreloadUdto(
            sid=preload.sid,
            filenames=preload.filenames,
            createdTime=preload.createdTime,
            expireTime=preload.expireTime
        )

    async def try_del_all(self) -> bool:
        f = True
        preloads = PreloadDoc.get_many()
        for preload in preloads:
            midf = await self.try_del_preload(preload)
            if midf is None:
                f = False
        return f

    async def try_get_preload(self, sid: str) -> PreloadDoc | None:
        f = PreloadDoc.try_get(SearchQuery.create_sid(sid))
        if f is None:
            return None
        return f

    async def try_get_preload_file_paths(
        self,
        preload_doc: PreloadDoc
    ) -> list[Path] | None:
        if not preload_doc or not preload_doc.filenames:
            return None

        paths: list[Path] = [
            Path(
                self._BasePreloadDir,
                preload_doc.sid,
                f
            ) for f in preload_doc.filenames
        ]

        return paths

    async def try_del_preload(self, preload: PreloadDoc) -> bool:
        preload = preload.refresh()
        preload.try_del()
        preload_dir = Path(self._BasePreloadDir, preload.sid)
        if not preload_dir.exists():
            log.err("if preload exists, its dir must exist")
            return False
        shutil.rmtree(
            preload_dir,
            ignore_errors=True
        )
        return True

    async def destroy(self):
        # cancel all going del tasks in any case
        for t in self._del_tasks:
            t.cancel()

        if self._cfg.must_clean_preloads_on_destroy:
            await self.try_del_all()

    async def _del_preload_on_expire(self, preload: PreloadDoc):
        await asyncio.sleep(preload.expireTime - preload.createdTime)
        log.info(f"{preload} is expired")
        await self.try_del_preload(preload)


async def handle_preload(
    webreq: aiohttp.web.BaseRequest
) -> aiohttp.web.StreamResponse:
    # warn: don't do that if you plan to receive large files!
    data = await webreq.post()

    rawfiles: list = data.getall("files")
    files: list[UploadFile] = []
    for f in rawfiles:
        if not isinstance(f, aiohttp.web.FileField):
            raise TypeError(
                f"all form data fields should be files, but got {f}"
            )
        files.append(UploadFile(
            filename=f.filename,
            buf=f.file,
            content_type=f.content_type
        ))

    udto = await PreloadSys.ie().preload(files)
    return aiohttp.web.json_response(udto.model_dump())

