from orwynn.base.errorhandler import ErrorHandler
from orwynn.http.errorhandler.middleware import ErrorHandlerHttpMiddleware
from orwynn.http.middleware.builtinmiddleware import BuiltinHttpMiddleware

from .context.middleware.builtin import ContextBuiltinMiddleware
from .context.middleware.contextbuiltin import (
    HttpRequestContextBuiltinMiddleware,
)
from .errorhandler.default import (
    DefaultErrorHandler,
    DefaultHttpErrorHandler,
    DefaultRequestValidationErrorHandler,
)

DEFAULT_HTTP_ERROR_HANDLERS: set[type[ErrorHandler]] = {
    DefaultErrorHandler,
    DefaultHttpErrorHandler,
    DefaultRequestValidationErrorHandler
}
"""
List of error handlers applied by default.
"""

# Order matters, the lowest index is initialized first.
BUILTIN_HTTP_MIDDLEWARE: list[type[BuiltinHttpMiddleware]] = [
    ErrorHandlerHttpMiddleware,
    ContextBuiltinMiddleware,
    HttpRequestContextBuiltinMiddleware
]
