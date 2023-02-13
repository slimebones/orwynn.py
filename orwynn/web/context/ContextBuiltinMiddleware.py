from orwynn import web
from orwynn.middleware.BuiltinMiddleware import BuiltinMiddleware
from orwynn.middleware.NextCallFn import NextCallFn
from orwynn.web.context.context_manager import context_manager


class ContextBuiltinMiddleware(BuiltinMiddleware):
    """Creates a shared context storage active within applied request-response
    cycle.
    """
    async def process(
        self, request: web.Request, call_next: NextCallFn
    ) -> web.Response:
        with context_manager():
            return await call_next(request)
