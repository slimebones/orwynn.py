from orwynn.error.ExceptionHandler import ExceptionHandler
from orwynn.proxy.BootProxy import BootProxy
from orwynn.web.http.HttpException import HttpException
from orwynn.web.http.requests import HttpRequest
from orwynn.web.http.responses import HttpResponse, JsonHttpResponse


class DefaultHttpExceptionHandler(ExceptionHandler):
    E = HttpException

    def handle(
        self, request: HttpRequest, error: HttpException
    ) -> HttpResponse:
        return JsonHttpResponse(
            BootProxy.ie().api_indication.digest(error),
            error.status_code
        )
