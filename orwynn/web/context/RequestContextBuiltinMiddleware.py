from orwynn import web
from orwynn.log.Log import Log
from orwynn.middleware.BuiltinMiddleware import BuiltinMiddleware
from orwynn.middleware.NextCallFn import NextCallFn
from orwynn.web.context.RequestContextId import RequestContextId


class RequestContextBuiltinMiddleware(BuiltinMiddleware):
    """Populates the context storage with the current request's id."""
    async def process(
        self, request: web.Request, call_next: NextCallFn
    ) -> web.Response:
        request_id: str = RequestContextId().save()

        # Also contextualize logs
        with Log.contextualize(request_id=request_id):
            return await call_next(request)
