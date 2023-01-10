from orwynn.app.ErrorHandler import ErrorHandler
from orwynn.proxy.BootProxy import BootProxy
from orwynn.web import HTTPException, JSONResponse, Request, Response


class DefaultHTTPExceptionHandler(ErrorHandler):
    E = HTTPException

    def handle(self, request: Request, error: HTTPException) -> Response:
        return JSONResponse(
            BootProxy.ie().api_indication.digest(error),
            error.status_code
        )
