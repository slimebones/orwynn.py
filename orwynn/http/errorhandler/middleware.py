from orwynn.base.errorhandler.errorhandler import ErrorHandler
from orwynn.http.middleware.builtinmiddleware import BuiltinHttpMiddleware
from orwynn.http.middleware.nextcall import HttpNextCall
from orwynn.http.requests import HttpRequest
from orwynn.http.responses import HttpResponse
from orwynn.utils import validation


class ErrorHandlerHttpMiddleware(BuiltinHttpMiddleware):
    """
    Handles all errors occured at Http layer.
    """
    def __init__(
        self,
        handlers: set[ErrorHandler]
    ) -> None:
        super().__init__()
        validation.validate_each(
            handlers, ErrorHandler, expected_sequence_type=set
        )
        self.__handlers: set[ErrorHandler] = handlers

    @property
    def handlers(self) -> set[ErrorHandler]:
        return self.__handlers.copy()

    async def process(
        self,
        request: HttpRequest,
        call_next: HttpNextCall
    ) -> HttpResponse:
        # Here no actions is done at the moment since handlers are added as
        # Starlette exception middleware.
        return await call_next(request)
