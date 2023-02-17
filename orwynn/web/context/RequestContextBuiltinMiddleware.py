from orwynn import web
from orwynn.log.Log import Log
from orwynn.middleware.BuiltinHttpMiddleware import BuiltinHttpMiddleware
from orwynn.middleware.HttpNextCall import HttpNextCall
from orwynn.web.context.RequestContextId import RequestContextId


class RequestContextBuiltinMiddleware(BuiltinHttpMiddleware):
    """Populates the context storage with the current request's id."""
    async def process(
        self, request: web.Request, call_next: HttpNextCall
    ) -> web.Response:
        request_id: str = RequestContextId().save()

        # Also contextualize logs
        with Log.contextualize(request_id=request_id):
            return await call_next(request)
