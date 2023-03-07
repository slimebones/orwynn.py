from orwynn.base.errorhandler import ErrorHandler
from orwynn.http._requests import HttpRequest
from orwynn.http._responses import HttpResponse, JsonHttpResponse
from orwynn.http.errors import HttpException
from orwynn.proxy.BootProxy import BootProxy
from orwynn.util.validation.errors import RequestValidationException


class DefaultRequestValidationErrorHandler(ErrorHandler):
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


class DefaultErrorHandler(ErrorHandler):
    E = Exception

    def handle(self, request: HttpRequest, error: Exception) -> HttpResponse:
        return JsonHttpResponse(
            BootProxy.ie().api_indication.digest(error),
            400
        )


class DefaultHttpErrorHandler(ErrorHandler):
    E = HttpException

    def handle(
        self, request: HttpRequest, error: HttpException
    ) -> HttpResponse:
        return JsonHttpResponse(
            BootProxy.ie().api_indication.digest(error),
            error.status_code
        )