from orwynn.http._context.HttpRequestContextId import HttpRequestContextId
from orwynn.http._middleware.BuiltinHttpMiddleware import BuiltinHttpMiddleware
from orwynn.http._middleware.HttpNextCall import HttpNextCall
from orwynn.http._requests import HttpRequest
from orwynn.http._responses import HttpResponse
from orwynn.log import Log


class HttpRequestContextBuiltinMiddleware(BuiltinHttpMiddleware):
    """Populates the context storage with the current request's id."""
    async def process(
        self, request: HttpRequest, call_next: HttpNextCall
    ) -> HttpResponse:
        request_id: str = HttpRequestContextId().save()

        # Also contextualize logs
        with Log.contextualize(**{"http.request_id": request_id}):
            return await call_next(request)
