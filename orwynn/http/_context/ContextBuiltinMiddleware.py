from orwynn.context.manager import context_manager
from orwynn.http._middleware.BuiltinHttpMiddleware import BuiltinHttpMiddleware
from orwynn.http._middleware.HttpNextCall import HttpNextCall
from orwynn.http._requests import HttpRequest
from orwynn.http._responses import HttpResponse


class ContextBuiltinMiddleware(BuiltinHttpMiddleware):
    """
    Creates a shared context storage active within applied request-response
    cycle.
    """
    async def process(
        self, request: HttpRequest, call_next: HttpNextCall
    ) -> HttpResponse:
        with context_manager():
            return await call_next(request)
