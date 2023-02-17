from orwynn import web
from orwynn.middleware.BuiltinWebsocketMiddleware import (
    BuiltinWebsocketMiddleware,
)
from orwynn.middleware.HttpNextCall import HttpNextCall
from orwynn.web.context.context_manager import context_manager


class ContextBuiltinWebsocketMiddleware(BuiltinWebsocketMiddleware):
    """Creates a shared context storage active within applied request-response
    cycle.
    """
    async def process(
        self, request: web.Request, call_next: HttpNextCall
    ) -> web.Response:
        with context_manager():
            return await call_next(request)
