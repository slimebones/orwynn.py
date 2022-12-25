from orwynn.app.ErrorHandler import ErrorHandler
from orwynn.log.Log import Log
from orwynn.proxy.BootProxy import BootProxy
from orwynn.util.validation import RequestValidationException
from orwynn.util.web import JSONResponse, Request, Response


class DefaultRequestValidationExceptionHandler(ErrorHandler):
    E = RequestValidationException
    log: Log

    def handle(
        self,
        request: Request,
        error: RequestValidationException
    ) -> Response:
        self.log.error(repr(error))
        return JSONResponse(
            BootProxy.ie().api_indication.digest(error),
            422
        )
