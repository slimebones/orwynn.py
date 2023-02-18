from orwynn.error.catching.ExceptionHandler import ExceptionHandler
from orwynn.error.Error import Error
from orwynn.web import JsonResponse, Request, Response


class DefaultErrorHandler(ExceptionHandler):
    E = Error

    def handle(self, request: Request, error: Error) -> Response:
        return JsonResponse(error.api, error.status_code)
