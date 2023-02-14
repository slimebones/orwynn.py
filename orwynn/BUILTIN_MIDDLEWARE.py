from orwynn.error.ErrorCatchMiddleware import ErrorCatchBuiltinMiddleware
from orwynn.middleware.BuiltinHttpMiddleware import BuiltinHttpMiddleware
from orwynn.web.context.ContextBuiltinMiddleware import (
    ContextBuiltinMiddleware,
)
from orwynn.web.context.RequestContextBuiltinMiddleware import (
    RequestContextBuiltinMiddleware,
)

# Order matters, the lowest index is initialized first
BUILTIN_MIDDLEWARE: list[type[BuiltinHttpMiddleware]] = [
    ErrorCatchBuiltinMiddleware,
    ContextBuiltinMiddleware,
    RequestContextBuiltinMiddleware
]
