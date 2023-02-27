from orwynn.http import BuiltinHttpMiddleware, HttpNextCall, HttpRequest, HttpResponse
from ...context._context_manager import context_manager


class ContextBuiltinMiddleware(BuiltinHttpMiddleware):
    """Creates a shared context storage active within applied request-response
    cycle.
    """
    async def process(
        self, request: HttpRequest, call_next: HttpNextCall
    ) -> HttpResponse:
        with context_manager():
            return await call_next(request)
