from orwynn.error.ExceptionHandler import ExceptionHandler
from orwynn.proxy.BootProxy import BootProxy
from orwynn.web.http.requests import HttpRequest
from orwynn.web.http.responses import HttpResponse, JsonHttpResponse


class DefaultExceptionHandler(ExceptionHandler):
    E = Exception

    def handle(self, request: HttpRequest, error: Exception) -> HttpResponse:
        return JsonHttpResponse(
            BootProxy.ie().api_indication.digest(error),
            400
        )
