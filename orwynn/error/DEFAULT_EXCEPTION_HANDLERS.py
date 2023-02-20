from orwynn.error.DefaultErrorHandler import DefaultErrorHandler
from orwynn.error.DefaultExceptionHandler import (
    DefaultExceptionHandler,
)
from orwynn.error.ExceptionHandler import ExceptionHandler
from orwynn.error.http.DefaultHttpExceptionHandler import (
    DefaultHttpExceptionHandler,
)
from orwynn.error.http.DefaultRequestValidationExceptionHandler import (
    DefaultRequestValidationExceptionHandler,
)
from orwynn.error.websocket.DefaultWebsocketErrorHandler import (
    DefaultWebsocketErrorHandler,
)
from orwynn.error.websocket.DefaultWebsocketExceptionHandler import (
    DefaultWebsocketExceptionHandler,
)

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
