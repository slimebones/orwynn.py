import os
from asyncio import Queue
from typing import Self

import pytest_asyncio
from rxcat import Conn, ConnArgs, ServerBusCfg, Transport

from orwynn import App, AppCfg, Cfg


@pytest_asyncio.fixture(autouse=True)
async def autorun():
    os.environ["ORWYNN_MODE"] = "test"
    os.environ["ORWYNN_DEBUG"] = "1"
    os.environ["ORWYNN_ALLOW_CLEAN"] = "1"

    yield
    await App.ie().destroy(is_hard=True)

def app_cfg() -> AppCfg:
    return AppCfg(
        server_bus_cfg=ServerBusCfg(
            transports=[
                Transport(
                    is_server=True,
                    conn_type=MockConn
                )
            ]))

class MockConn(Conn[None]):
    def __init__(self, args: ConnArgs[None]) -> None:
        super().__init__(args)
        self.inp_queue: Queue[dict] = Queue()
        self.out_queue: Queue[dict] = Queue()

    def __aiter__(self) -> Self:
        return self

    async def __anext__(self) -> dict:
        return await self.recv()

    async def recv(self) -> dict:
        return await self.inp_queue.get()

    async def send(self, data: dict):
        await self.out_queue.put(data)

    async def close(self):
        self._is_closed = True

    async def client__send(self, data: dict):
        await self.inp_queue.put(data)

    async def client__recv(self) -> dict:
        return await self.out_queue.get()

@pytest_asyncio.fixture
async def app(cfg: AppCfg) -> App:
    app = await App().init(cfg)
    return app

class MockCfg(Cfg):
    num: int
