import asyncio
import os
from asyncio import Queue
from typing import Self

import pytest
import pytest_asyncio
from pydantic import BaseModel

from orwynn import App, AppCfg, Cfg
from orwynn.yon.server import BusCfg, Con, ConArgs, Transport


@pytest_asyncio.fixture(autouse=True)
async def autorun():
    os.environ["ORWYNN_MODE"] = "test"
    os.environ["ORWYNN_DEBUG"] = "1"
    os.environ["ORWYNN_ALLOW_CLEAN"] = "1"

    yield
    await App.ie().destroy()

@pytest.fixture
def app_cfg() -> AppCfg:
    return AppCfg(
        bus_cfg=BusCfg(
            transports=[
                Transport(
                    is_server=True,
                    con_type=MockCon
                )
            ],
            reg_regular_codes=[Mock_1]),
        extend_cfg_pack={
            "test": [
                MockCfg(num=1)
            ]
        })

class MockCon(Con[None]):
    def __init__(self, args: ConArgs[None] = ConArgs(core=None)) -> None:
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

    async def client_send(self, data: dict):
        await self.inp_queue.put(data)

    async def client_recv(self, timeout: float = 1.0) -> dict:
        return await asyncio.wait_for(self.out_queue.get(), timeout)

@pytest_asyncio.fixture
async def app(app_cfg: AppCfg) -> App:
    app = await App().init(app_cfg)
    return app

class MockCfg(Cfg):
    num: int

class Mock_1(BaseModel):
    key: str

    @staticmethod
    def code():
        return "orwynn_test::mock_1"
