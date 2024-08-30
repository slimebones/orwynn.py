# from aiohttp.web import WebSocketResponse as AiohttpWebsocket

# from yon.server._transport import Con, ConArgs


class Udp:
    pass
# class Udp(Con[TConMsg]):
#     def __init__(self, args: ConArgs[AiohttpWebsocket]) -> None:
#         super().__init__(args)

#     async def receive_json(self) -> WsMsg:
#         return await self._core.receive()

#     async def send_bytes(self, data: bytes):
#         return await self._core.send_bytes(data)

#     async def send_json(self, data: dict):
#         return await self._core.send_json(data)

#     async def send_str(self, data: str):
#         return await self._core.send_str(data)

#     async def close(self):
#         return await self._core.close()
