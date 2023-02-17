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
# Note that before that error handler middleware is initialized.
BUILTIN_HTTP_MIDDLEWARE: list[type[BuiltinHttpMiddleware]] = [
    ContextBuiltinMiddleware,
    RequestContextBuiltinMiddleware
]

BUILTIN_WEBSOCKET_MIDDLEWARE: list[type[BuiltinWebsocketMiddleware]] = [
    ConnectionBuiltinWebsocketMiddleware,
    ContextBuiltinWebsocketMiddleware,
    RequestContextBuiltinWebsocketMiddleware
]
