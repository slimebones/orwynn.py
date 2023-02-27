from ._exchandler.DefaultWebsocketErrorHandler import DefaultWebsocketErrorHandler
from ._exchandler.DefaultWebsocketExceptionHandler import DefaultWebsocketExceptionHandler
from orwynn.base.exchandler import ExceptionHandler

DEFAULT_WEBSOCKET_EXCEPTION_HANDLERS: set[type[ExceptionHandler]] = {
    DefaultWebsocketExceptionHandler,
    DefaultWebsocketErrorHandler
}
