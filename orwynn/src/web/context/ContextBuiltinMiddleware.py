from orwynn.src.middleware.BuiltinHttpMiddleware import BuiltinHttpMiddleware
from orwynn.src.middleware.HttpNextCall import HttpNextCall
from orwynn.src.web.context.context_manager import context_manager
from orwynn.src.web.http.requests import HttpRequest
from orwynn.src.web.http.responses import HttpResponse


class ContextBuiltinMiddleware(BuiltinHttpMiddleware):
    """Creates a shared context storage active within applied request-response
    cycle.
    """
    async def process(
        self, request: HttpRequest, call_next: HttpNextCall
    ) -> HttpResponse:
        with context_manager():
            return await call_next(request)
