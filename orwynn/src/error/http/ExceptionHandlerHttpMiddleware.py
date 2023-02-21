from orwynn import validation
from orwynn.src.error.ExceptionHandler import ExceptionHandler
from orwynn.src.middleware.BuiltinHttpMiddleware import BuiltinHttpMiddleware
from orwynn.src.middleware.HttpNextCall import HttpNextCall
from orwynn.src.web.http.requests import HttpRequest
from orwynn.src.web.http.responses import HttpResponse


class ExceptionHandlerHttpMiddleware(BuiltinHttpMiddleware):
    """
    Handles all errors occured at Http layer.
    """
    def __init__(
        self,
        handlers: set[ExceptionHandler]
    ) -> None:
        super().__init__()
        validation.validate_each(
            handlers, ExceptionHandler, expected_sequence_type=set
        )
        self.__handlers: set[ExceptionHandler] = handlers

    @property
    def handlers(self) -> set[ExceptionHandler]:
        return self.__handlers.copy()

    async def process(
        self,
        request: HttpRequest,
        call_next: HttpNextCall
    ) -> HttpResponse:
        # Here no actions is done at the moment since handlers are added as
        # Starlette exception middleware.
        return await call_next(request)
