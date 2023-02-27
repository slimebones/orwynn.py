from ._exchandler.default import DefaultErrorHandler, DefaultExceptionHandler, DefaultHttpExceptionHandler, DefaultRequestValidationExceptionHandler
from orwynn.base.exchandler import ExceptionHandler

# List of error handlers applied by default
DEFAULT_HTTP_EXCEPTION_HANDLERS: set[type[ExceptionHandler]] = {
    DefaultExceptionHandler,
    DefaultErrorHandler,
    DefaultHttpExceptionHandler,
    DefaultRequestValidationExceptionHandler
}
