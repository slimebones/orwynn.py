from orwynn.log.log import Log
from orwynn.websocket._context.id import (
    WebsocketRequestContextId,
)
from orwynn.websocket._middleware.builtin import (
    BuiltinWebsocketMiddleware,
)
from orwynn.websocket._middleware.nextcall import WebsocketNextCall
from orwynn.websocket.websocket import Websocket


class RequestContextBuiltinWebsocketMiddleware(BuiltinWebsocketMiddleware):
    """Populates the context storage with the current request's id."""
    async def process(
        self, request: Websocket, call_next: WebsocketNextCall
    ) -> None:
        request_id: str = WebsocketRequestContextId().save()

        # Also contextualize logs
        with Log.contextualize(**{"websocket.request_id": request_id}):
            return await call_next(request)
