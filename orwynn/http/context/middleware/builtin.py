from orwynn.context.manager import context_manager
from orwynn.http.middleware.builtinmiddleware import BuiltinHttpMiddleware
from orwynn.http.middleware.nextcall import HttpNextCall
from orwynn.http.requests import HttpRequest
from orwynn.http.responses import HttpResponse


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
