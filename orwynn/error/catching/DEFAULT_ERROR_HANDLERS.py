from orwynn.error.catching.DefaultErrorHandler import DefaultErrorHandler
from orwynn.error.catching.DefaultExceptionHandler import \
    DefaultExceptionHandler
from orwynn.error.catching.DefaultHttpExceptionHandler import \
    DefaultHttpExceptionHandler
from orwynn.error.catching.DefaultRequestValidationExceptionHandler import \
    DefaultRequestValidationExceptionHandler
from orwynn.error.catching.ErrorHandler import ErrorHandler

# List of error handlers applied by default
DEFAULT_ERROR_HANDLERS: set[type[ErrorHandler]] = {
    DefaultExceptionHandler,
    DefaultErrorHandler,
    DefaultHttpExceptionHandler,
    DefaultRequestValidationExceptionHandler
}
