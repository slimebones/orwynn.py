from orwynn import web
from orwynn.middleware.BuiltinHttpMiddleware import BuiltinHttpMiddleware
from orwynn.middleware.HttpNextCallFn import HttpNextCallFn
from orwynn.web.context.context_manager import context_manager


class ContextBuiltinMiddleware(BuiltinHttpMiddleware):
    """Creates a shared context storage active within applied request-response
    cycle.
    """
    async def process(
        self, request: web.Request, call_next: HttpNextCallFn
    ) -> web.Response:
        with context_manager():
            return await call_next(request)
