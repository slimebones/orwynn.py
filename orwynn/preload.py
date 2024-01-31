"""
Manages preloaded files, i.e. files that need to be loaded before the main
instruction send.
"""
import asyncio
from io import BufferedIOBase
import shutil
from pathlib import Path
import typing

import aiofiles
import aiohttp.web
from pydantic import BaseModel
from pykit.dt import DTUtils
from pykit.err import InpErr
from pykit.log import log
from orwynn.cfg import Cfg
from orwynn.sys import Sys
from orwynn.mongo import Doc

class PreloadUdto(BaseModel):
    sid: str
    filenames: list[str]
    created_time: float
    expire_time: float

class PreloadDoc(Doc):
    filenames: list[str]
    created_time: float
    expire_time: float


class UploadFile(BaseModel):
    filename: str
    buf: BufferedIOBase
    content_type: str

    class Config:
        arbitrary_types_allowed = True


class PreloadCfg(Cfg):
    must_clean_on_destroy: bool = False


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
            created_time=DTUtils.get_utc_timestamp(),
            expire_time=DTUtils.get_delta_timestamp(
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

        preload = preload.upd({
            "$set": {
                "filenames": preload.filenames
            }
        })

        return PreloadUdto(
            sid=preload.sid,
            filenames=preload.filenames,
            created_time=preload.created_time,
            expire_time=preload.expire_time
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
        f = PreloadDoc.try_get({"sid": sid})
        if f is None:
            return None
        return f

    async def try_get_preload_file_paths(self, sid: str) -> list[Path] | None:
        pl = await self.try_get_preload(sid)
        if not pl or not pl.filenames:
            return None

        paths: list[Path] = []
        for f in pl.filenames:
            paths.append(Path(self._BasePreloadDir, sid, f))

        return paths

    async def try_del_preload(self, preload: PreloadDoc) -> bool:
        preload = preload.refresh()
        preload_dir = Path(self._BasePreloadDir, preload.sid)
        assert \
            preload_dir.exists(), "if preload exists, its dir must exist"
        shutil.rmtree(
            preload_dir,
            ignore_errors=True
        )
        return True

    async def destroy(self):
        if self._cfg.must_clean_on_destroy:
            raise ValueError("wow")
            await self.try_del_all()

    async def _del_preload_on_expire(self, preload: PreloadDoc):
        await asyncio.sleep(preload.expire_time - preload.created_time)
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
            raise ValueError(
                f"all form data fields should be files, but got {f}"
            )
        files.append(UploadFile(
            filename=f.filename,
            buf=f.file,
            content_type=f.content_type
        ))

    udto = await PreloadSys.ie().preload(files)
    return aiohttp.web.json_response(udto.model_dump())

