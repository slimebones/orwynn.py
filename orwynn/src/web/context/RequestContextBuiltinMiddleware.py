from orwynn.src.log.Log import Log
from orwynn.src.middleware.BuiltinHttpMiddleware import BuiltinHttpMiddleware
from orwynn.src.middleware.HttpNextCall import HttpNextCall
from orwynn.src.web.context.RequestContextId import RequestContextId
from orwynn.src.web.http.requests import HttpRequest
from orwynn.src.web.http.responses import HttpResponse


class RequestContextBuiltinMiddleware(BuiltinHttpMiddleware):
    """Populates the context storage with the current request's id."""
    async def process(
        self, request: HttpRequest, call_next: HttpNextCall
    ) -> HttpResponse:
        request_id: str = RequestContextId().save()

        # Also contextualize logs
        with Log.contextualize(**{"http.request_id": request_id}):
            return await call_next(request)
