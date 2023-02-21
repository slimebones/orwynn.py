from orwynn.src.error.DefaultErrorHandler import DefaultErrorHandler
from orwynn.src.error.DefaultExceptionHandler import (
    DefaultExceptionHandler,
)
from orwynn.src.error.ExceptionHandler import ExceptionHandler
from orwynn.src.error.http.DefaultHttpExceptionHandler import (
    DefaultHttpExceptionHandler,
)
from orwynn.src.error.http.DefaultRequestValidationExceptionHandler import (
    DefaultRequestValidationExceptionHandler,
)
from orwynn.src.error.websocket.DefaultWebsocketErrorHandler import (
    DefaultWebsocketErrorHandler,
)
from orwynn.src.error.websocket.DefaultWebsocketExceptionHandler import (
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
