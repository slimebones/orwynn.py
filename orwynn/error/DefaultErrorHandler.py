from orwynn.error.Error import Error
from orwynn.error.ExceptionHandler import ExceptionHandler
from orwynn.web import JsonResponse, Request, Response


class DefaultErrorHandler(ExceptionHandler):
    E = Error

    def handle(self, request: Request, error: Error) -> Response:
        return JsonResponse(error.api, 400)
