from types import NoneType

from orwynn import validation, web
from orwynn.error.catching.ExceptionHandler import ExceptionHandler
from orwynn.log.Log import Log
from orwynn.middleware.BuiltinWebsocketMiddleware import (
    BuiltinWebsocketMiddleware,
)
from orwynn.middleware.WebsocketNextCall import WebsocketNextCall


class ExceptionHandlerBuiltinWebsocketMiddleware(BuiltinWebsocketMiddleware):
    """
    Handles all errors occured at Websocket layer.
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

    async def process(
        self,
        request: web.Websocket,
        call_next: WebsocketNextCall
    ) -> None:
        try:
            await call_next(request)
        except Exception as err:
            # Choose according handler
            for handler in self.__handlers:
                if isinstance(err, handler.HandledException):
                    validation.apply(
                        handler.handle(request, err),
                        NoneType
                    )
                else:
                    # Not recommended to raise an error since it won't be
                    # logged properly at this layer, better to explicitly log
                    Log.error(
                        "malfunction at ExceptionHandler middleware"
                        " for websocket connection: no handler to handle an"
                        f" error {err}"
                    )
