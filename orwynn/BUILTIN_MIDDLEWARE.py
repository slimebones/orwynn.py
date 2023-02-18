from orwynn.error.catching.ExceptionHandlerBuiltinHttpMiddleware import ExceptionHandlerBuiltinHttpMiddleware
from orwynn.error.catching.ExceptionHandlerBuiltinWebsocketMiddleware import ExceptionHandlerBuiltinWebsocketMiddleware
from orwynn.middleware.BuiltinHttpMiddleware import BuiltinHttpMiddleware
from orwynn.middleware.BuiltinWebsocketMiddleware import (
    BuiltinWebsocketMiddleware,
)
from orwynn.web.context.ContextBuiltinMiddleware import (
    ContextBuiltinMiddleware,
)
from orwynn.web.context.ContextBuiltinWebsocketMiddleware import (
    ContextBuiltinWebsocketMiddleware,
)
from orwynn.web.context.RequestContextBuiltinMiddleware import (
    RequestContextBuiltinMiddleware,
)
from orwynn.web.context.RequestContextBuiltinWebsocketMiddleware import (
    RequestContextBuiltinWebsocketMiddleware,
)
from orwynn.web.websocket.ConnectionBuiltinWebsocketMiddleware import (
    ConnectionBuiltinWebsocketMiddleware,
)

# Order matters, the lowest index is initialized first.
BUILTIN_HTTP_MIDDLEWARE: list[type[BuiltinHttpMiddleware]] = [
    ExceptionHandlerBuiltinHttpMiddleware,
    ContextBuiltinMiddleware,
    RequestContextBuiltinMiddleware
]

BUILTIN_WEBSOCKET_MIDDLEWARE: list[type[BuiltinWebsocketMiddleware]] = [
    # Connection middleware should be first, since the exception handlers will
    # access websocket object
    ConnectionBuiltinWebsocketMiddleware,
    ExceptionHandlerBuiltinWebsocketMiddleware,
    ContextBuiltinWebsocketMiddleware,
    RequestContextBuiltinWebsocketMiddleware
]
