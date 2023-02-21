from orwynn.error.Error import Error
from orwynn.error.ExceptionHandler import ExceptionHandler
from orwynn.web.http.requests import HttpRequest
from orwynn.web.http.responses import HttpResponse, JsonHttpResponse


class DefaultErrorHandler(ExceptionHandler):
    E = Error

    def handle(self, request: HttpRequest, error: Error) -> HttpResponse:
        return JsonHttpResponse(error.api, 400)
