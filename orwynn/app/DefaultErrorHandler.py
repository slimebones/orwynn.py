from typing import Any
from orwynn.app.ErrorHandler import ErrorHandler
from orwynn.base.error.Error import Error
from orwynn.log.LogService import LogService
from orwynn.util.web import JSONResponse, Request, Response


class DefaultErrorHandler(ErrorHandler):
    E = Error

    def __init__(self, log: LogService, **data: Any) -> None:
        self.log = log
        super().__init__(**data)

    def handle(self, request: Request, error: Error) -> Response:
        self.log.error(error)
        return JSONResponse(error.api, 400)
