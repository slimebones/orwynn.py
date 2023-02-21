from orwynn.src.middleware.HttpNextCall import HttpNextCall
from orwynn.src.middleware.Middleware import Middleware
from orwynn.src.web.http.requests import HttpRequest
from orwynn.src.web.http.responses import HttpResponse


class HttpMiddleware(Middleware):
    """Intermediate operational layer for HTTP requests."""
    async def dispatch(
        self,
        request: HttpRequest,
        call_next: HttpNextCall
    ) -> HttpResponse:
        return await super().dispatch(request, call_next)

    async def process(
        self,
        request: HttpRequest,
        call_next: HttpNextCall
    ) -> HttpResponse:
        return await super().process(request, call_next)
