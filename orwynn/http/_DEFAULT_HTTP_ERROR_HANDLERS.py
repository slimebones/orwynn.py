from orwynn.base.errorhandler import ErrorHandler

from ._errorhandler.default import (
    DefaultErrorHandler,
    DefaultHttpErrorHandler,
    DefaultRequestValidationErrorHandler,
)

# List of error handlers applied by default
DEFAULT_HTTP_ERROR_HANDLERS: set[type[ErrorHandler]] = {
    DefaultErrorHandler,
    DefaultHttpErrorHandler,
    DefaultRequestValidationErrorHandler
}
""""""
