from orwynn import web
from orwynn.middleware.BuiltinWebsocketMiddleware import (
    BuiltinWebsocketMiddleware,
)
from orwynn.middleware.WebsocketNextCall import WebsocketNextCall


class ConnectionBuiltinWebsocketMiddleware(BuiltinWebsocketMiddleware):
    """Manages websocket's connection acceptance.

    Note that you don't need to use websocket.accept() anywhere in your program
    or you will stuck in an endless loop. But you can call websocket.close()
    whenever you want (multiple calls don't raise any exceptions).

    Maybe, in future there will be a possibility to disable this Middleware
    (and thus accept a connection everywhere you want).
    """

    async def process(
        self, request: web.Websocket, call_next: WebsocketNextCall
    ) -> None:
        await request.accept()
        await call_next(request)
