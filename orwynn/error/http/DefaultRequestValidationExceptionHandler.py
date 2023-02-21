from orwynn.error.ExceptionHandler import ExceptionHandler
from orwynn.proxy.BootProxy import BootProxy
from orwynn.validation import RequestValidationException
from orwynn.web.http.requests import HttpRequest
from orwynn.web.http.responses import HttpResponse, JsonHttpResponse


class DefaultRequestValidationExceptionHandler(ExceptionHandler):
    E = RequestValidationException

    def handle(
        self,
        request: HttpRequest,
        error: RequestValidationException
    ) -> HttpResponse:
        return JsonHttpResponse(
            BootProxy.ie().api_indication.digest(error),
            422
        )
