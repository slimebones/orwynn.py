from orwynn.base.exchandler import ExceptionHandler

from ._exchandler.default import (
    DefaultExceptionHandler,
    DefaultHttpExceptionHandler,
    DefaultRequestValidationExceptionHandler,
)

# List of error handlers applied by default
DEFAULT_HTTP_EXCEPTION_HANDLERS: set[type[ExceptionHandler]] = {
    DefaultExceptionHandler,
    DefaultHttpExceptionHandler,
    DefaultRequestValidationExceptionHandler
}
