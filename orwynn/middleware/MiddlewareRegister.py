from typing import Callable, Optional, Sequence
from orwynn.BUILTIN_MIDDLEWARE import BUILTIN_HTTP_MIDDLEWARE, BUILTIN_WEBSOCKET_MIDDLEWARE
from orwynn.error.catching.ExceptionHandler import ExceptionHandler
from orwynn.error.catching.ExceptionHandlerBuiltinHttpMiddleware import ExceptionHandlerBuiltinHttpMiddleware
from orwynn.error.catching.ExceptionHandlerBuiltinWebsocketMiddleware import ExceptionHandlerBuiltinWebsocketMiddleware
from orwynn.error.catching.ExceptionHandlerManager import ExceptionHandlerManager
from orwynn.middleware.BuiltinHttpMiddleware import BuiltinHttpMiddleware
from orwynn.middleware.BuiltinWebsocketMiddleware import BuiltinWebsocketMiddleware
from orwynn.middleware.Middleware import Middleware
from orwynn.web.http.Cors import Cors
from orwynn.web.Protocol import Protocol


class MiddlewareRegister:
    """
    Registers middleware to the system.

    Note that exception handlers is transforming into united middleware which
    handles all errors occured for a protocol.
    """
    def __init__(
        self,
        middleware_register: Callable
    ) -> None:
        self.__middleware_register: Callable = middleware_register

    def register(
        self,
        user_middleware: list[Middleware],
        user_exception_handlers: set[ExceptionHandler],
        *,
        cors: Optional[Cors]
    ) -> None:
        populated_handlers_py_protocol: dict[
            Protocol, set[ExceptionHandler]
        ] = ExceptionHandlerManager().get_populated_handlers_by_protocol(
            user_exception_handlers
        )

        # FIXME: Here below the builtin middleware are created directly without
        #   the Di notifying which may raise a confusion in the next calls.
        #   Also it might become harder to support if an builtin middleware
        #   requests any Di-related dependency.

        http_builtin_middleware: Sequence[
            BuiltinHttpMiddleware
        ] = self.__collect_http_builtin_middleware(
            populated_handlers_py_protocol[Protocol.HTTP]
        )
        websocket_builtin_middleware: Sequence[
            BuiltinWebsocketMiddleware
        ] = self.__collect_websocket_builtin_middleware(
            populated_handlers_py_protocol[Protocol.WEBSOCKET]
        )

        self.__middleware_register(
            # Add builtin middlewares first, and others second. No matters the
            # order between middleware of different protocols.
            http_builtin_middleware
            + websocket_builtin_middleware
            + user_middleware,
            cors=cors
        )

    def __collect_http_builtin_middleware(
        self,
        handlers: set[ExceptionHandler]
    ) -> list[BuiltinHttpMiddleware]:
        middleware_arr: list[BuiltinHttpMiddleware] = []

        for Middleware_ in BUILTIN_HTTP_MIDDLEWARE:
            if issubclass(Middleware_, ExceptionHandlerBuiltinHttpMiddleware):
                middleware_arr.append(Middleware_(
                    handlers
                ))
            else:
                middleware_arr.append(Middleware_())

        return middleware_arr

    def __collect_websocket_builtin_middleware(
        self,
        handlers: set[ExceptionHandler]
    ) -> list[BuiltinWebsocketMiddleware]:
        middleware_arr: list[BuiltinWebsocketMiddleware] = []

        for Middleware_ in BUILTIN_WEBSOCKET_MIDDLEWARE:
            if issubclass(
                Middleware_, ExceptionHandlerBuiltinWebsocketMiddleware
            ):
                middleware_arr.append(Middleware_(
                    handlers
                ))
            else:
                middleware_arr.append(Middleware_())

        return middleware_arr
