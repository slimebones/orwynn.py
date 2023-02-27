from orwynn.http import BuiltinHttpMiddleware, ExceptionHandlerHttpMiddleware
from ._context.ContextBuiltinMiddleware import (
    ContextBuiltinMiddleware,
)
from ._context.HttpRequestContextBuiltinMiddleware import (
    HttpRequestContextBuiltinMiddleware
)

# Order matters, the lowest index is initialized first.
BUILTIN_HTTP_MIDDLEWARE: list[type[BuiltinHttpMiddleware]] = [
    ExceptionHandlerHttpMiddleware,
    ContextBuiltinMiddleware,
    HttpRequestContextBuiltinMiddleware
]
