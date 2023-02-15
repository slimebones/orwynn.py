from orwynn.error.ErrorCatchBuiltinMiddleware import (
    ErrorCatchBuiltinMiddleware,
)
from orwynn.error.ErrorCatchBuiltinWebsocketMiddleware import (
    ErrorCatchBuiltinWebsocketMiddleware,
)
from orwynn.middleware.BuiltinHttpMiddleware import BuiltinHttpMiddleware
from orwynn.middleware.BuiltinWebsocketMiddleware import (
    BuiltinWebsocketMiddleware,
)
from orwynn.web.context.ContextBuiltinMiddleware import (
    ContextBuiltinMiddleware,
)
from orwynn.web.context.RequestContextBuiltinMiddleware import (
    RequestContextBuiltinMiddleware,
)
from orwynn.web.websocket.ConnectionBuiltinWebsocketMiddleware import (
    ConnectionBuiltinWebsocketMiddleware,
)

# Order matters, the lowest index is initialized first
BUILTIN_HTTP_MIDDLEWARE: list[type[BuiltinHttpMiddleware]] = [
    ErrorCatchBuiltinMiddleware,
    ContextBuiltinMiddleware,
    RequestContextBuiltinMiddleware
]

BUILTIN_WEBSOCKET_MIDDLEWARE: list[type[BuiltinWebsocketMiddleware]] = [
    ConnectionBuiltinWebsocketMiddleware,
    ErrorCatchBuiltinWebsocketMiddleware
]
