from orwynn.base.errorhandler._ErrorHandler import ErrorHandler
from orwynn.http._middleware.BuiltinHttpMiddleware import BuiltinHttpMiddleware
from orwynn.http._middleware.HttpNextCall import HttpNextCall
from orwynn.http._requests import HttpRequest
from orwynn.http._responses import HttpResponse
from orwynn.util import validation


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
