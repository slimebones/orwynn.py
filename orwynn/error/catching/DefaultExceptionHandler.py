from orwynn.error.catching.ErrorHandler import ErrorHandler
from orwynn.proxy.BootProxy import BootProxy
from orwynn.web import JSONResponse, Request, Response


class DefaultExceptionHandler(ErrorHandler):
    E = Exception

    def handle(self, request: Request, error: Exception) -> Response:
        print(1)
        return JSONResponse(BootProxy.ie().api_indication.digest(error), 400)
