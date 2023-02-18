import inspect
from types import NoneType

from orwynn import validation, web
from orwynn.error.MalfunctionError import MalfunctionError
from orwynn.error.catching.ExceptionHandler import ExceptionHandler
from orwynn.log.Log import Log
from orwynn.log.WebsocketLogger import WebsocketLogger
from orwynn.middleware.BuiltinWebsocketMiddleware import (
    BuiltinWebsocketMiddleware,
)
from orwynn.middleware.WebsocketNextCall import WebsocketNextCall
from orwynn.web.context.WebsocketRequestContextId import WebsocketRequestContextId


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

    @property
    def handlers(self) -> set[ExceptionHandler]:
        return self.__handlers.copy()

    async def process(
        self,
        request: web.Websocket,
        call_next: WebsocketNextCall
    ) -> None:
        try:
            await call_next(request)
        except Exception as err:
            is_handled: bool = False
            malfunction_message: str = \
                "malfunction at ExceptionHandler middleware" \
                " for a websocket connection: no handler to handle an" \
                f" error {err}"

            # Choose according handler
            for handler in self.__handlers:
                if isinstance(err, handler.HandledException):
                    if not inspect.iscoroutinefunction(handler.handle):
                        malfunction_message = \
                            f"handler function {handler.handle} is not a" \
                            " coroutine"
                        break
                    else:
                        validation.apply(
                            await handler.handle(request, err),
                            NoneType
                        )
                        is_handled = True

            if not is_handled:
                # Not recommended to raise an error since it won't be
                # logged properly at this layer, better to explicitly log and
                # digest the error on the fly.
                data: dict = MalfunctionError(malfunction_message).api
                await WebsocketLogger().log_response(
                    data,
                    request=request,
                    request_id=WebsocketRequestContextId().get()
                )
                await request.send_json(
                    data
                )

            # Close the request after handling (even on malfunction error),
            # otherwise it will be stuck
            await request.close()
