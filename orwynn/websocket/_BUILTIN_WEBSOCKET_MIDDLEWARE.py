from ._context.ContextBuiltinWebsocketMiddleware import \
    ContextBuiltinWebsocketMiddleware
from ._context.RequestContextBuiltinWebsocketMiddleware import \
    RequestContextBuiltinWebsocketMiddleware
from ._exchandler.ExceptionHandlerWebsocketMiddleware import \
    ExceptionHandlerWebsocketMiddleware
from ._middleware.BuiltinWebsocketMiddleware import BuiltinWebsocketMiddleware

BUILTIN_WEBSOCKET_MIDDLEWARE: list[type[BuiltinWebsocketMiddleware]] = [
    # Connection middleware should be first, since the exception handlers will
    # access websocket object
    ContextBuiltinWebsocketMiddleware,
    ExceptionHandlerWebsocketMiddleware,
    ContextBuiltinWebsocketMiddleware,
    RequestContextBuiltinWebsocketMiddleware
]
