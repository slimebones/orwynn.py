from orwynn.http.context.id import HttpRequestContextId
from orwynn.http.middleware.builtinmiddleware import BuiltinHttpMiddleware
from orwynn.http.middleware.nextcall import HttpNextCall
from orwynn.http.requests import HttpRequest
from orwynn.http.responses import HttpResponse
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
