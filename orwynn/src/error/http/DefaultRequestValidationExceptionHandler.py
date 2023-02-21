from orwynn.src.error.ExceptionHandler import ExceptionHandler
from orwynn.src.proxy.BootProxy import BootProxy
from orwynn.src.validation import RequestValidationException
from orwynn.src.web.http.requests import HttpRequest
from orwynn.src.web.http.responses import HttpResponse, JsonHttpResponse


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
