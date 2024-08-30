from typing import Self

from aiohttp import WSMsgType
from aiohttp.web import WebSocketResponse as AiohttpWebsocket

from orwynn.yon.server.transport import Con, ConArgs


class Ws(Con[AiohttpWebsocket]):
    def __init__(self, args: ConArgs[AiohttpWebsocket]) -> None:
        super().__init__(args)

    def __aiter__(self) -> Self:
        return self

    async def __anext__(self) -> dict:
        conmsg = await self._core.receive()
        if conmsg.type in (
                WSMsgType.CLOSE, WSMsgType.CLOSING, WSMsgType.CLOSED):
            raise StopAsyncIteration
        return conmsg.json()

    async def recv(self) -> dict:
        return await self._core.receive_json()

    async def send(self, data: dict):
        return await self._core.send_json(data)

    async def close(self):
        return await self._core.close()
