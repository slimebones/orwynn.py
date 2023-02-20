
from orwynn import validation, web
from orwynn.error.ExceptionHandler import ExceptionHandler
from orwynn.middleware.BuiltinHttpMiddleware import BuiltinHttpMiddleware
from orwynn.middleware.HttpNextCall import HttpNextCall


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
        request: web.Request,
        call_next: HttpNextCall
    ) -> web.Response:
        # Here no actions is done at the moment since handlers are added as
        # Starlette exception middleware.
        return await call_next(request)
