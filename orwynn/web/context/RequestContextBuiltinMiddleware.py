from orwynn import web
from orwynn.middleware.BuiltinMiddleware import BuiltinMiddleware
from orwynn.middleware.NextCallFn import NextCallFn
from orwynn.web.context.RequestContextId import RequestContextId


class RequestContextBuiltinMiddleware(BuiltinMiddleware):
    """Populates the context storage with the current request's id."""
    async def process(
        self, request: web.Request, call_next: NextCallFn
    ) -> web.Response:
        RequestContextId().save()
        return await call_next(request)
