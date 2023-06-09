import inspect
from types import NoneType

from orwynn.base.error.errors import MalfunctionError
from orwynn.base.error.utils import (
    find_detailed_class_for_exception,
)
from orwynn.base.errorhandler.errorhandler import ErrorHandler
from orwynn.utils import validation
from orwynn.websocket.context.id import (
    WebsocketRequestContextId,
)
from orwynn.websocket.log.logger import WebsocketLogger
from orwynn.websocket.middleware.builtin import (
    BuiltinWebsocketMiddleware,
)
from orwynn.websocket.middleware.nextcall import WebsocketNextCall
from orwynn.websocket.websocket import Websocket


class ErrorHandlerWebsocketMiddleware(BuiltinWebsocketMiddleware):
    """
    Handles all errors occured at Websocket layer.
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
        request: Websocket,
        call_next: WebsocketNextCall
    ) -> None:
        try:
            await call_next(request)
        except Exception as err:  # noqa: BLE001
            is_handled: bool = False
            malfunction_message: str = \
                "malfunction at ErrorHandler middleware" \
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
