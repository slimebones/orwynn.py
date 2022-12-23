from orwynn import app
from orwynn.base.error.Error import Error
from orwynn.util.web import JSONResponse, Request, Response


class DefaultErrorHandler(app.ErrorHandler):
    E = Error

    def handle(self, request: Request, error: Error) -> Response:
        return JSONResponse(error.api, 400)
