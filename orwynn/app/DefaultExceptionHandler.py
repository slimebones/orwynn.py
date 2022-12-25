from orwynn.app.ErrorHandler import ErrorHandler
from orwynn.base.error import get_non_framework_exceptions
from orwynn.log import log
from orwynn.util import validation
from orwynn.util.web import JSONResponse, Request, Response
from orwynn.proxy.BootProxy import BootProxy


class DefaultExceptionHandler(ErrorHandler):
    E = get_non_framework_exceptions()

    def handle(self, request: Request, error: Exception) -> Response:
        log.error(repr(error))
        return JSONResponse(BootProxy.ie().api_indication.digest(error), 400)

    def set_handled_exception(
        self, E: type[Exception] | list[type[Exception]]
    ) -> None:
        if isinstance(E, list):
            validation.validate_each(E, Exception)
        else:
            validation.validate(E, Exception)

        self.__class__.E = E
