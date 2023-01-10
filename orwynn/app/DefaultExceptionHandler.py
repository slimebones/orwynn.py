from orwynn.app.ErrorHandler import ErrorHandler
from orwynn.error.get_non_framework_exceptions import \
    get_non_framework_exceptions
from orwynn.proxy.BootProxy import BootProxy
from orwynn import validation
from orwynn.web import JSONResponse, Request, Response


class DefaultExceptionHandler(ErrorHandler):
    E = get_non_framework_exceptions()

    def handle(self, request: Request, error: Exception) -> Response:
        return JSONResponse(BootProxy.ie().api_indication.digest(error), 400)

    def set_handled_exception(
        self, E: type[Exception] | list[type[Exception]]
    ) -> None:
        if isinstance(E, list):
            validation.validate_each(E, Exception)
        else:
            validation.validate(E, Exception)

        self.__class__.E = E
