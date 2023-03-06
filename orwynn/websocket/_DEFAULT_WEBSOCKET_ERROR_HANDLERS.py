from orwynn.base.errorhandler import ErrorHandler

from ._errorhandler.DefaultWebsocketErrorHandler import (
    DefaultWebsocketErrorHandler,
)

DEFAULT_WEBSOCKET_EXCEPTION_HANDLERS: set[type[ErrorHandler]] = {
    DefaultWebsocketErrorHandler,
}
