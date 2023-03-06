from orwynn.http._errorhandler.ErrorHandlerHttpMiddleware import (
    ErrorHandlerHttpMiddleware,
)
from orwynn.http._middleware.BuiltinHttpMiddleware import BuiltinHttpMiddleware

from ._context.ContextBuiltinMiddleware import ContextBuiltinMiddleware
from ._context.HttpRequestContextBuiltinMiddleware import (
    HttpRequestContextBuiltinMiddleware,
)

# Order matters, the lowest index is initialized first.
BUILTIN_HTTP_MIDDLEWARE: list[type[BuiltinHttpMiddleware]] = [
    ErrorHandlerHttpMiddleware,
    ContextBuiltinMiddleware,
    HttpRequestContextBuiltinMiddleware
]
