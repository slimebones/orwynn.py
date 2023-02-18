from orwynn.error.catching.ExceptionHandler import ExceptionHandler
from orwynn.proxy.BootProxy import BootProxy
from orwynn.web import JsonResponse, Request, Response


class DefaultExceptionHandler(ExceptionHandler):
    E = Exception

    def handle(self, request: Request, error: Exception) -> Response:
        return JsonResponse(BootProxy.ie().api_indication.digest(error), 400)
