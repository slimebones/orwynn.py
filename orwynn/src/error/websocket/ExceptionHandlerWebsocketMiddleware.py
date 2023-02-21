import inspect
from types import NoneType

from orwynn import validation
from orwynn.src.error.ExceptionHandler import ExceptionHandler
from orwynn.src.error.find_detailed_class_for_exception import (
    find_detailed_class_for_exception,
)
from orwynn.src.error.MalfunctionError import MalfunctionError
from orwynn.src.log.WebsocketLogger import WebsocketLogger
from orwynn.src.middleware.BuiltinWebsocketMiddleware import (
    BuiltinWebsocketMiddleware,
)
from orwynn.src.middleware.WebsocketNextCall import WebsocketNextCall
from orwynn.src.web.context.WebsocketRequestContextId import (
    WebsocketRequestContextId,
)
from orwynn.src.web.websocket.Websocket import Websocket


class ExceptionHandlerWebsocketMiddleware(BuiltinWebsocketMiddleware):
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
        request: Websocket,
        call_next: WebsocketNextCall
    ) -> None:
        try:
            await call_next(request)
        except Exception as err:  # noqa: BLE001
            is_handled: bool = False
            malfunction_message: str = \
                "malfunction at ExceptionHandler middleware" \
                " for a websocket connection: no handler to handle an" \
                f" error {err}"

            # Choose according handler
            AppropriateException: type[Exception] = \
                find_detailed_class_for_exception(
                    err,
                    [handler.HandledException for handler in self.__handlers]
                )
            for handler in self.__handlers:
                if handler.HandledException is AppropriateException:
                    if not isinstance(err, handler.HandledException):
                        malfunction_message = \
                            f"appropriate Exception {AppropriateException}" \
                            f" is not a parent for actual exception {err}"
                    elif not inspect.iscoroutinefunction(handler.handle):
                        malfunction_message = \
                            f"handler function {handler.handle} is not a" \
                            " coroutine"
                    else:
                        validation.apply(
                            await handler.handle(request, err),
                            NoneType
                        )
                        is_handled = True

                    # Finally exit after the first match
                    break

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
