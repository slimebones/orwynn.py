from orwynn.error.catching.DefaultErrorHandler import DefaultErrorHandler
from orwynn.error.catching.DefaultExceptionHandler import \
    DefaultExceptionHandler
from orwynn.error.catching.DefaultHttpExceptionHandler import \
    DefaultHttpExceptionHandler
from orwynn.error.catching.DefaultRequestValidationExceptionHandler import \
    DefaultRequestValidationExceptionHandler
from orwynn.error.catching.ExceptionHandler import ExceptionHandler

# List of error handlers applied by default
DEFAULT_EXCEPTION_HANDLERS: set[type[ExceptionHandler]] = {
    DefaultExceptionHandler,
    DefaultErrorHandler,
    DefaultHttpExceptionHandler,
    DefaultRequestValidationExceptionHandler
}
