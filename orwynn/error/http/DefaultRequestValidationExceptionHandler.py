from orwynn.error.ExceptionHandler import ExceptionHandler
from orwynn.proxy.BootProxy import BootProxy
from orwynn.validation import RequestValidationException
from orwynn.web import JsonResponse, Request, Response


class DefaultRequestValidationExceptionHandler(ExceptionHandler):
    E = RequestValidationException

    def handle(
        self,
        request: Request,
        error: RequestValidationException
    ) -> Response:
        return JsonResponse(
            BootProxy.ie().api_indication.digest(error),
            422
        )
