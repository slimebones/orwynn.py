from orwynn.base.exchandler import ExceptionHandler

from ._exchandler.DefaultWebsocketExceptionHandler import (
    DefaultWebsocketExceptionHandler,
)

DEFAULT_WEBSOCKET_EXCEPTION_HANDLERS: set[type[ExceptionHandler]] = {
    DefaultWebsocketExceptionHandler,
}
