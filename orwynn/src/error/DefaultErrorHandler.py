from orwynn.src.error.Error import Error
from orwynn.src.error.ExceptionHandler import ExceptionHandler
from orwynn.src.web.http.requests import HttpRequest
from orwynn.src.web.http.responses import HttpResponse, JsonHttpResponse


class DefaultErrorHandler(ExceptionHandler):
    E = Error

    def handle(self, request: HttpRequest, error: Error) -> HttpResponse:
        return JsonHttpResponse(error.api, 400)
