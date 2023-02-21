from orwynn.src.error.ExceptionHandler import ExceptionHandler
from orwynn.src.proxy.BootProxy import BootProxy
from orwynn.src.web.http.HttpException import HttpException
from orwynn.src.web.http.requests import HttpRequest
from orwynn.src.web.http.responses import HttpResponse, JsonHttpResponse


class DefaultHttpExceptionHandler(ExceptionHandler):
    E = HttpException

    def handle(
        self, request: HttpRequest, error: HttpException
    ) -> HttpResponse:
        return JsonHttpResponse(
            BootProxy.ie().api_indication.digest(error),
            error.status_code
        )
