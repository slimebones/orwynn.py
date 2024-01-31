"""
Manages preloaded files, i.e. files that need to be loaded before the main
instruction send.
"""
import asyncio
import shutil
from contextlib import suppress
from pathlib import Path

import aiofiles
from pydantic import BaseModel
from pykit.dt import DTUtils

class PreloadUdto(BaseModel):
    sid: str
    filenames: list[str]
    created_time: float
    expire_time: float

class PreloadDoc(Document):
    filenames: list[str]
    created_time: float
    expire_time: float


class PreloadSys(Sys):
    # All preloaded files are stored in var/preload dir, under corresponding
    # dir with preload_sid name. Every stored file has it's original filename.

    _DefaultExpirationDelta = 3600.0 # = 1 hour

    async def init(self):
        self._BasePreloadDir = Path(
            BootProxy.ie().root_dir,
            "var/preload"
        )
        self._del_tasks: set[asyncio.Task] = set()

    async def preload(self, ufiles: list[UploadFile]) -> PreloadUdto:
        if not ufiles:
            raise InpErr("empty ufile list")

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

        preload_target_dir = Path(self._BasePreloadDir, preload.getid())
        preload_target_dir.mkdir(parents=True, exist_ok=True)

        for ufile in ufiles:
            if not ufile.filename:
                raise InpErr("ufile with empty filename")

            preload.filenames.append(ufile.filename)
            save_path = Path(preload_target_dir, ufile.filename)
            async with aiofiles.open(save_path, "wb+") as out_file:
                content: bytes = await ufile.read()
                await ufile.close()
                await out_file.write(content)

        preload = preload.update(
            set={
                "filenames": preload.filenames
            }
        )
        return PreloadUdto(
            sid=preload.getid(),
            filenames=preload.filenames,
            created_time=preload.created_time,
            expire_time=preload.expire_time
        )

    async def try_del_all(self) -> bool:
        res = True
        preloads = PreloadDoc.get()
        for preload in preloads:
            midres = await self.try_del_preload(preload)
            if not midres:
                res = False
        return res

    async def try_get_preload(self, sid: str) -> PreloadDoc | None:
        res = list(PreloadDoc.get({"id": sid}))

        if not res:
            return None

        assert len(res) == 1
        return res[0]

    async def try_get_preload_file_paths(self, sid: str) -> list[Path] | None:
        pl = await self.try_get_preload(sid)
        if not pl or not pl.filenames:
            return None

        paths: list[Path] = []
        for f in pl.filenames:
            paths.append(Path(self._BasePreloadDir, sid, f))

        return paths

    async def try_del_preload(self, preload: PreloadDoc) -> bool:
        with suppress(DatabaseEntityNotFoundError):
            preload = preload.refresh()
            preload_dir = Path(self._BasePreloadDir, preload.getid())
            assert \
                preload_dir.exists(), "if preload exists, its dir must exist"
            shutil.rmtree(
                preload_dir,
                ignore_errors=True
            )
            return True
        return False

    async def _del_preload_on_expire(self, preload: PreloadDoc):
        await asyncio.sleep(preload.expire_time - preload.created_time)
        Log.info(f"{preload} is expired")
        await self.try_del_preload(preload)


class PreloadCtrl(HttpController):
    Route = "/"
    Endpoints = [
        Endpoint(
            method="post"
        )
    ]

    async def post(self, files: list[UploadFile]) -> dict:
        return (await PreloadSys.ie().preload(files)).api


module = Module(
    "/preload",
    Controllers=[PreloadCtrl]
)
