from types import NoneType

from orwynn import validation, web
from orwynn.error.MalfunctionError import MalfunctionError
from orwynn.error.catching.ExceptionHandler import ExceptionHandler
from orwynn.log.Log import Log
from orwynn.middleware.BuiltinHttpMiddleware import BuiltinHttpMiddleware
from orwynn.middleware.HttpNextCall import HttpNextCall


class ExceptionHandlerBuiltinHttpMiddleware(BuiltinHttpMiddleware):
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
        try:
            return await call_next(request)
        except Exception as err:
            # Choose according handler
            for handler in self.__handlers:
                if isinstance(err, handler.HandledException):
                    return validation.apply(
                        handler.handle(request, err),
                        web.Response
                    )
            raise MalfunctionError(
                f"no handler to handle an error {err}"
            )
