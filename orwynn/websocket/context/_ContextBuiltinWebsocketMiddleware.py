from orwynn.websocket import (
    BuiltinWebsocketMiddleware
)
from orwynn.http import HttpNextCall, HttpRequest, HttpResponse
from orwynn.context._context_manager import context_manager


class ContextBuiltinWebsocketMiddleware(BuiltinWebsocketMiddleware):
    """Creates a shared context storage active within applied request-response
    cycle.
    """
    async def process(
        self, request: HttpRequest, call_next: HttpNextCall
    ) -> HttpResponse:
        with context_manager():
            return await call_next(request)
