from orwynn.app.ErrorHandler import ErrorHandler
from orwynn.log.Log import Log
from orwynn.proxy.BootProxy import BootProxy
from orwynn.util.web import HTTPException, JSONResponse, Request, Response


class DefaultHTTPExceptionHandler(ErrorHandler):
    E = HTTPException
    log: Log

    def handle(self, request: Request, error: HTTPException) -> Response:
        self.log.error(repr(error))
        return JSONResponse(
            BootProxy.ie().api_indication.digest(error),
            error.status_code
        )
