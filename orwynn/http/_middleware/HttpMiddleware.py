from orwynn.base.middleware import Middleware
from orwynn.http._requests import HttpRequest
from orwynn.http._responses import HttpResponse
from orwynn.http._middleware.HttpNextCall import HttpNextCall


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
