from orwynn.base.errorhandler import ErrorHandler
from orwynn.websocket.middleware.connectionbuiltin import (
    ConnectionBuiltinWebsocketMiddleware,
)

from .context.middleware.builtin import (
    ContextBuiltinWebsocketMiddleware,
)
from .context.middleware.contextbuiltin import (
    RequestContextBuiltinWebsocketMiddleware,
)
from .errorhandler.default import (
    DefaultWebsocketErrorHandler,
)
from .errorhandler.middleware import (
    ErrorHandlerWebsocketMiddleware,
)
from .middleware.builtin import BuiltinWebsocketMiddleware

DEFAULT_WEBSOCKET_EXCEPTION_HANDLERS: set[type[ErrorHandler]] = {
    DefaultWebsocketErrorHandler,
}

BUILTIN_WEBSOCKET_MIDDLEWARE: list[type[BuiltinWebsocketMiddleware]] = [
    # Connection middleware should be first, since the exception handlers will
    # access websocket object
    ConnectionBuiltinWebsocketMiddleware,
    ContextBuiltinWebsocketMiddleware,
    ErrorHandlerWebsocketMiddleware,
    RequestContextBuiltinWebsocketMiddleware
]
