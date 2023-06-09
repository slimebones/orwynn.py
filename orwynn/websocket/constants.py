from orwynn.websocket._middleware.connectionbuiltin import (
    ConnectionBuiltinWebsocketMiddleware,
)

from ._context.middleware.builtin import (
    ContextBuiltinWebsocketMiddleware,
)
from ._context.middleware.contextbuiltin import (
    RequestContextBuiltinWebsocketMiddleware,
)
from ._errorhandler.middleware import (
    ErrorHandlerWebsocketMiddleware,
)
from ._middleware.builtin import BuiltinWebsocketMiddleware
from orwynn.base.errorhandler import ErrorHandler

from ._errorhandler.default import (
    DefaultWebsocketErrorHandler,
)

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
