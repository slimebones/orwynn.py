import asyncio
from asyncio import Queue
from contextvars import ContextVar
from typing import Self

import pytest_asyncio
from pydantic import BaseModel
from ryz.core import Ok, Res, Err
from yon.server import (
    Bus,
    BusCfg,
    Con,
    ConArgs,
    Transport,
)


class Mock_1(BaseModel):
    num: int

    @staticmethod
    def code() -> str:
        return "yon::mock_1"

class Mock_2(BaseModel):
    num: int

    @staticmethod
    def code() -> str:
        return "yon::mock_2"

class EmptyMock(BaseModel):
    @staticmethod
    def code() -> str:
        return "yon::empty_mock"

@pytest_asyncio.fixture(autouse=True)
async def auto():
    yield
    Bus.subfn_init_queue.clear()
    await Bus.destroy()

@pytest_asyncio.fixture
async def sbus() -> Bus:
    bus = Bus.ie()
    cfg = BusCfg(
        transports=[
            Transport(
                is_server=True,
                con_type=MockCon)
        ],
        reg_types=[
            Mock_1,
            Mock_2,
            EmptyMock
        ])
    await asyncio.wait_for(bus.init(cfg), 1)
    return bus

class MockCon(Con[None]):
    def __init__(self, args: ConArgs[None]) -> None:
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

yon_mock_ctx = ContextVar("yon_mock", default={})
class MockCtxManager:
    async def __aenter__(self):
        yon_mock_ctx.set({"name": "hello"})
    async def __aexit__(self, *args):
        return

async def get_mock_ctx_manager_for_msg(_) -> Res[MockCtxManager]:
    return Ok(MockCtxManager())

async def get_mock_ctx_manager_for_srpc_send(_) -> Res[MockCtxManager]:
    return Ok(MockCtxManager())

def find_codeid_in_welcome_rbmsg(code: str, rbmsg: dict) -> Res[int]:
    for i, code_container in enumerate(rbmsg["msg"]["codes"]):
        if code in code_container:
            return Ok(i)
    return Err(code)
