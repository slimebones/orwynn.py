from orwynn.http import BuiltinHttpMiddleware, ExceptionHandlerHttpMiddleware
from orwynn.websocket import (
    BuiltinWebsocketMiddleware,
    ExceptionHandlerWebsocketMiddleware
)
from orwynn.http.context._ContextBuiltinMiddleware import (
    ContextBuiltinMiddleware,
)
from orwynn.websocket.context._ContextBuiltinWebsocketMiddleware import (
    ContextBuiltinWebsocketMiddleware,
)
from orwynn.http.context._HttpRequestContextBuiltinMiddleware import (
    HttpRequestContextBuiltinMiddleware,
)
from orwynn.websocket.context._RequestContextBuiltinWebsocketMiddleware import (
    RequestContextBuiltinWebsocketMiddleware,
)
from orwynn.websocket import _ConnectionBuiltinWebsocketMiddleware

# Order matters, the lowest index is initialized first.
BUILTIN_HTTP_MIDDLEWARE: list[type[BuiltinHttpMiddleware]] = [
    ExceptionHandlerHttpMiddleware,
    ContextBuiltinMiddleware,
    HttpRequestContextBuiltinMiddleware
]

BUILTIN_WEBSOCKET_MIDDLEWARE: list[type[BuiltinWebsocketMiddleware]] = [
    # Connection middleware should be first, since the exception handlers will
    # access websocket object
    _ConnectionBuiltinWebsocketMiddleware,
    ExceptionHandlerWebsocketMiddleware,
    ContextBuiltinWebsocketMiddleware,
    RequestContextBuiltinWebsocketMiddleware
]
