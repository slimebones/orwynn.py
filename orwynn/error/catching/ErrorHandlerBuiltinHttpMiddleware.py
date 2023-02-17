from orwynn import validation, web
from orwynn.error.catching.ErrorHandler import ErrorHandler
from orwynn.middleware.BuiltinHttpMiddleware import BuiltinHttpMiddleware
from orwynn.middleware.HttpNextCallFn import HttpNextCallFn


class ErrorHandlerBuiltinHttpMiddleware(BuiltinHttpMiddleware):
    """
    Handles all errors occured at HTTP layers.
    """
    def __init__(
        self,
        handler: ErrorHandler
    ) -> None:
        super().__init__()

        validation.validate(handler, ErrorHandler)
        self.__handler: ErrorHandler = handler

    async def process(
        self,
        request: web.Request,
        call_next: HttpNextCallFn
    ) -> web.Response:
        try:
            a = await super().process(request, call_next)
            return a
        except self.__handler.HandledException as err:
            return validation.apply(
                self.__handler.handle(request, err),
                web.Response
            )
