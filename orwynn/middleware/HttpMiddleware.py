from orwynn import web
from orwynn.middleware.HttpNextCallFn import HttpNextCallFn
from orwynn.middleware.Middleware import Middleware


class HttpMiddleware(Middleware):
    """Intermediate operational layer for HTTP requests."""
    async def dispatch(
        self,
        request: web.Request,
        call_next: HttpNextCallFn
    ) -> web.Response:
        return await super().dispatch(request, call_next)

    async def process(
        self,
        request: web.Request,
        call_next: HttpNextCallFn
    ) -> web.Response:
        return await super().process(request, call_next)
