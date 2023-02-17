from types import NoneType

from orwynn import validation, web
from orwynn.error.catching.ErrorHandler import ErrorHandler
from orwynn.middleware.BuiltinWebsocketMiddleware import (
    BuiltinWebsocketMiddleware,
)
from orwynn.middleware.WebsocketNextCallFn import WebsocketNextCallFn


class ErrorHandlerBuiltinWebsocketMiddleware(BuiltinWebsocketMiddleware):
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
        request: web.Websocket,
        call_next: WebsocketNextCallFn
    ) -> None:
        try:
            await super().process(request, call_next)
        except self.__handler.HandledException as err:
            validation.apply(
                self.__handler.handle(request, err),
                NoneType
            )
