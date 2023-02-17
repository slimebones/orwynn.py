from orwynn.error.catching.ExceptionHandler import ExceptionHandler
from orwynn.proxy.BootProxy import BootProxy
from orwynn.web import HttpException, JSONResponse, Request, Response


class DefaultHttpExceptionHandler(ExceptionHandler):
    E = HttpException

    def handle(self, request: Request, error: HttpException) -> Response:
        return JSONResponse(
            BootProxy.ie().api_indication.digest(error),
            error.status_code
        )
