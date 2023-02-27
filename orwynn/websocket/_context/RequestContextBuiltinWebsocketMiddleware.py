from orwynn.log._Log import Log
from orwynn.websocket._context.WebsocketRequestContextId import \
    WebsocketRequestContextId
from orwynn.websocket._middleware.BuiltinWebsocketMiddleware import \
    BuiltinWebsocketMiddleware
from orwynn.websocket._middleware.WebsocketNextCall import WebsocketNextCall
from orwynn.websocket._Websocket import Websocket


class RequestContextBuiltinWebsocketMiddleware(BuiltinWebsocketMiddleware):
    """Populates the context storage with the current request's id."""
    async def process(
        self, request: Websocket, call_next: WebsocketNextCall
    ) -> None:
        request_id: str = WebsocketRequestContextId().save()

        # Also contextualize logs
        with Log.contextualize(**{"websocket.request_id": request_id}):
            return await call_next(request)
