from orwynn import web
from orwynn.log.Log import Log
from orwynn.middleware.BuiltinWebsocketMiddleware import (
    BuiltinWebsocketMiddleware,
)
from orwynn.middleware.WebsocketNextCallFn import WebsocketNextCallFn
from orwynn.web.context.WebsocketRequestContextId import (
    WebsocketRequestContextId,
)


class RequestContextBuiltinWebsocketMiddleware(BuiltinWebsocketMiddleware):
    """Populates the context storage with the current request's id."""
    async def process(
        self, request: web.Websocket, call_next: WebsocketNextCallFn
    ) -> None:
        request_id: str = WebsocketRequestContextId().save()

        # Also contextualize logs
        with Log.contextualize(websocket_request_id=request_id):
            return await call_next(request)
