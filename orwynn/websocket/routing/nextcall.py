import contextlib

from orwynn.utils.url import UrlVars
from orwynn.websocket.websocket import Websocket

from .handlers import DispatchWebsocketHandler, WebsocketHandler
from .helpers import get_handler_kwargs


class NextCallHandler:
    """
    Propagates calls through the given handler list.
    """
    def __init__(
        self,
        handlers: list[WebsocketHandler],
        url_vars: UrlVars
    ) -> None:
        # Index of function being executed
        self.__current_index: int = 0
        self.__handlers: list[WebsocketHandler] = handlers
        self.__url_vars: UrlVars = url_vars

    async def __call__(self, websocket: Websocket) -> None:
        """
        Propagates a call to the next recipient in the function list.
        """
        # Supress: End of the stack, just pass
        with contextlib.suppress(KeyError):
            current_handler: WebsocketHandler = \
                self.__handlers[self.__current_index]
            # For dispatch handlers recreate self and delegate execution right
            # to the new instance using rest available handlers
            if isinstance(current_handler, DispatchWebsocketHandler):
                if self.__current_index == len(self.__handlers) - 1:
                    raise ValueError(
                        "last element of handlers cannot be a dispatch handler"
                        f" {current_handler}"
                    )

                await current_handler.fn(
                    websocket,
                    self.__class__(
                        handlers=self.__handlers[self.__current_index+1:],
                        url_vars=self.__url_vars
                    )
                )
            else:
                await current_handler.fn(
                    websocket,
                    **get_handler_kwargs(current_handler, self.__url_vars)
                )
