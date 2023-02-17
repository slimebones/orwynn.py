from orwynn.error.catching.ExceptionHandler import ExceptionHandler
from orwynn.proxy.BootProxy import BootProxy
from orwynn.web import JSONResponse, Request, Response


class DefaultExceptionHandler(ExceptionHandler):
    E = Exception

    def handle(self, request: Request, error: Exception) -> Response:
        return JSONResponse(BootProxy.ie().api_indication.digest(error), 400)
