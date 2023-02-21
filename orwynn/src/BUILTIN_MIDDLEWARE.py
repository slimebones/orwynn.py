from orwynn.src.error.http.ExceptionHandlerHttpMiddleware import (
    ExceptionHandlerHttpMiddleware,
)
from orwynn.src.error.websocket.ExceptionHandlerWebsocketMiddleware import (
    ExceptionHandlerWebsocketMiddleware,
)
from orwynn.src.middleware.BuiltinHttpMiddleware import BuiltinHttpMiddleware
from orwynn.src.middleware.BuiltinWebsocketMiddleware import (
    BuiltinWebsocketMiddleware,
)
from orwynn.src.web.context.ContextBuiltinMiddleware import (
    ContextBuiltinMiddleware,
)
from orwynn.src.web.context.ContextBuiltinWebsocketMiddleware import (
    ContextBuiltinWebsocketMiddleware,
)
from orwynn.src.web.context.RequestContextBuiltinMiddleware import (
    RequestContextBuiltinMiddleware,
)
from orwynn.src.web.context.RequestContextBuiltinWebsocketMiddleware import (
    RequestContextBuiltinWebsocketMiddleware,
)
from orwynn.src.web.websocket.ConnectionBuiltinWebsocketMiddleware import (
    ConnectionBuiltinWebsocketMiddleware,
)

# Order matters, the lowest index is initialized first.
BUILTIN_HTTP_MIDDLEWARE: list[type[BuiltinHttpMiddleware]] = [
    ExceptionHandlerHttpMiddleware,
    ContextBuiltinMiddleware,
    RequestContextBuiltinMiddleware
]

BUILTIN_WEBSOCKET_MIDDLEWARE: list[type[BuiltinWebsocketMiddleware]] = [
    # Connection middleware should be first, since the exception handlers will
    # access websocket object
    ConnectionBuiltinWebsocketMiddleware,
    ExceptionHandlerWebsocketMiddleware,
    ContextBuiltinWebsocketMiddleware,
    RequestContextBuiltinWebsocketMiddleware
]
