from orwynn.websocket._middleware.BuiltinWebsocketMiddleware import (
    BuiltinWebsocketMiddleware,
)
from orwynn.websocket._middleware.WebsocketNextCall import WebsocketNextCall
from orwynn.websocket._Websocket import Websocket


class ConnectionBuiltinWebsocketMiddleware(BuiltinWebsocketMiddleware):
    """Manages websocket's connection acceptance.

    Note that you don't need to use websocket.accept() anywhere in your program
    or you will stuck in an endless loop. But you can call websocket.close()
    whenever you want (multiple calls don't raise any exceptions).

    Maybe, in future there will be a possibility to disable this Middleware
    (and thus accept a connection everywhere you want).
    """

    async def process(
        self, request: Websocket, call_next: WebsocketNextCall
    ) -> None:
        await request.accept()
        await call_next(request)
