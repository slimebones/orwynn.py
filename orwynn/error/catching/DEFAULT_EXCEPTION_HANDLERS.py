from orwynn.error.catching.DefaultErrorHandler import DefaultErrorHandler
from orwynn.error.catching.DefaultExceptionHandler import \
    DefaultExceptionHandler
from orwynn.error.catching.DefaultHttpExceptionHandler import \
    DefaultHttpExceptionHandler
from orwynn.error.catching.DefaultRequestValidationExceptionHandler import \
    DefaultRequestValidationExceptionHandler
from orwynn.error.catching.DefaultWebsocketErrorHandler import DefaultWebsocketErrorHandler
from orwynn.error.catching.DefaultWebsocketExceptionHandler import DefaultWebsocketExceptionHandler
from orwynn.error.catching.ExceptionHandler import ExceptionHandler

# List of error handlers applied by default
DEFAULT_HTTP_EXCEPTION_HANDLERS: set[type[ExceptionHandler]] = {
    DefaultExceptionHandler,
    DefaultErrorHandler,
    DefaultHttpExceptionHandler,
    DefaultRequestValidationExceptionHandler
}


DEFAULT_WEBSOCKET_EXCEPTION_HANDLERS: set[type[ExceptionHandler]] = {
    DefaultWebsocketExceptionHandler,
    DefaultWebsocketErrorHandler
}
