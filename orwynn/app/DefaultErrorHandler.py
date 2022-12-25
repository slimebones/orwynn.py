from orwynn.app.ErrorHandler import ErrorHandler
from orwynn.base.error.Error import Error
from orwynn.log import log
from orwynn.util.web import JSONResponse, Request, Response


class DefaultErrorHandler(ErrorHandler):
    E = Error

    def handle(self, request: Request, error: Error) -> Response:
        log.error(error)
        return JSONResponse(error.api, 400)
