from orwynn.http.exchandler._DefaultErrorHandler import DefaultErrorHandler
from orwynn.http.exchandler._DefaultExceptionHandler import (
    DefaultExceptionHandler,
)
from orwynn.base.exchandler._ExceptionHandler import ExceptionHandler
from orwynn.base.error.http.DefaultHttpExceptionHandler import (
    DefaultHttpExceptionHandler,
)
from orwynn.base.error.http.DefaultRequestValidationExceptionHandler import (
    DefaultRequestValidationExceptionHandler,
)
from orwynn.base.error.websocket.DefaultWebsocketErrorHandler import (
    DefaultWebsocketErrorHandler,
)
from orwynn.base.error.websocket.DefaultWebsocketExceptionHandler import (
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
