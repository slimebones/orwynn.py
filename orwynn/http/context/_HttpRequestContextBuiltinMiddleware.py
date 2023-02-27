from orwynn.http import (BuiltinHttpMiddleware, HttpNextCall, HttpRequest,
                         HttpResponse)
from orwynn.http.context._HttpRequestContextId import HttpRequestContextId
from orwynn.log.Log import Log


class HttpRequestContextBuiltinMiddleware(BuiltinHttpMiddleware):
    """Populates the context storage with the current request's id."""
    async def process(
        self, request: HttpRequest, call_next: HttpNextCall
    ) -> HttpResponse:
        request_id: str = HttpRequestContextId().save()

        # Also contextualize logs
        with Log.contextualize(**{"http.request_id": request_id}):
            return await call_next(request)
