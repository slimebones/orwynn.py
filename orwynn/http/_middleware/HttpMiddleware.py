from orwynn.base import Middleware
from orwynn.http import HttpRequest, HttpResponse, HttpNextCall


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
