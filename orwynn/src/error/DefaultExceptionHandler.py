from orwynn.src.error.ExceptionHandler import ExceptionHandler
from orwynn.src.proxy.BootProxy import BootProxy
from orwynn.src.web.http.requests import HttpRequest
from orwynn.src.web.http.responses import HttpResponse, JsonHttpResponse


class DefaultExceptionHandler(ExceptionHandler):
    E = Exception

    def handle(self, request: HttpRequest, error: Exception) -> HttpResponse:
        return JsonHttpResponse(
            BootProxy.ie().api_indication.digest(error),
            400
        )
