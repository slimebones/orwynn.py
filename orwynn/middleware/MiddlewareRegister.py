from typing import Any, Callable, Sequence

from fastapi.middleware.cors import CORSMiddleware as FastAPI_CORSMiddleware
from starlette.middleware.base import \
    BaseHTTPMiddleware as StarletteBaseHTTPMiddleware

from orwynn import validation
from orwynn.app.App import App
from orwynn.BUILTIN_MIDDLEWARE import (BUILTIN_HTTP_MIDDLEWARE,
                                       BUILTIN_WEBSOCKET_MIDDLEWARE)
from orwynn.error.DefaultExceptionHandler import DefaultExceptionHandler
from orwynn.error.ExceptionHandler import ExceptionHandler
from orwynn.error.ExceptionHandlerManager import ExceptionHandlerManager
from orwynn.error.get_exception_direct_subclasses import get_exception_direct_subclasses
from orwynn.error.http.DefaultHttpExceptionHandler import DefaultHttpExceptionHandler
from orwynn.error.http.ExceptionHandlerHttpMiddleware import \
    ExceptionHandlerHttpMiddleware
from orwynn.error.websocket.ExceptionHandlerWebsocketMiddleware import \
    ExceptionHandlerWebsocketMiddleware
from orwynn.middleware.BuiltinHttpMiddleware import BuiltinHttpMiddleware
from orwynn.middleware.BuiltinWebsocketMiddleware import \
    BuiltinWebsocketMiddleware
from orwynn.middleware.HttpMiddleware import HttpMiddleware
from orwynn.middleware.Middleware import Middleware
from orwynn.middleware.WebsocketMiddleware import WebsocketMiddleware
from orwynn.router.WebsocketHandler import DispatchWebsocketHandler
from orwynn.router.WebsocketStack import WebsocketStack
from orwynn.web import HttpException
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
        *,
        app: App,
        middleware_arr: list[Middleware],
        exception_handlers: list[ExceptionHandler],
        cors: Cors | None,
        websocket_stack: WebsocketStack,
    ) -> None:
        self.__app: App = app

        self.__middleware_arr: list[Middleware] = middleware_arr
        self.__exception_handlers: set[ExceptionHandler] = set(
            exception_handlers
        )

        self.__cors: Cors | None = cors
        self.__websocket_stack: WebsocketStack = websocket_stack

    def register_all(self) -> None:
        """
        Registers all middleware to the system.
        """
        populated_handlers_py_protocol: dict[
            Protocol, set[ExceptionHandler]
        ] = ExceptionHandlerManager().get_populated_handlers_by_protocol(
            self.__exception_handlers
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

        self.__register_middleware_arr(
            # Add builtin middlewares first, and others second. No matters the
            # order between middleware of different protocols.
            http_builtin_middleware
            + websocket_builtin_middleware
            + self.__middleware_arr
        )

    def __collect_http_builtin_middleware(
        self,
        handlers: set[ExceptionHandler]
    ) -> list[BuiltinHttpMiddleware]:
        middleware_arr: list[BuiltinHttpMiddleware] = []

        for Middleware_ in BUILTIN_HTTP_MIDDLEWARE:
            if issubclass(Middleware_, ExceptionHandlerHttpMiddleware):
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
                Middleware_, ExceptionHandlerWebsocketMiddleware
            ):
                middleware_arr.append(Middleware_(
                    handlers
                ))
            else:
                middleware_arr.append(Middleware_())

        return middleware_arr

    def __register_middleware_arr(
        self,
        middleware_arr: Sequence[Middleware],
    ) -> None:
        """
        Adds middleware to the system.

        Args:
            middleware_arr:
                Middleware list to be added to the system.
            cors:
                Cors object (can be None) to configure the Cors middleware on
                the fly.
        """
        # Note that middleware here is reversed since Starlette.add_middleware
        # inserts new functions at the top of the middleware list which makes
        # older added middlewares executable last, which is not logical.
        #
        # But this reversion should be executed only for HtppMiddleware since
        # for Websockets we have own logic.
        #
        # So, first task is to separate middleware
        http_middleware_arr: list[HttpMiddleware] = []
        websocket_middleware_arr: list[WebsocketMiddleware] = []

        for middleware in middleware_arr:
            if isinstance(middleware, HttpMiddleware):
                http_middleware_arr.append(middleware)
            elif isinstance(middleware, WebsocketMiddleware):
                websocket_middleware_arr.append(middleware)
            elif type(middleware) is Middleware:
                raise TypeError(
                    f"cannot register an instance {middleware} of an abstact"
                    " class Middleware"
                )
            else:
                raise TypeError(
                    f"unrecognized middleware {middleware}"
                )

        # Add CORS middleware first
        self.__register_cors_middleware()

        # Add HTTP from reversed list to comply Starlette
        for http_middleware in reversed(http_middleware_arr):
            self.__register_middleware_unit(http_middleware)

        # Add Websocket normally
        if websocket_middleware_arr != []:
            if self.__is_websocket_middleware_added:
                raise ValueError(
                    "websocket middleware have been already added"
                )

            for websocket_middleware in websocket_middleware_arr:
                self.__register_middleware_unit(websocket_middleware)

            self.__is_websocket_middleware_added = True

    def __register_middleware_unit(self, middleware: Middleware) -> None:
        validation.validate(middleware, Middleware)

        # Note that dispatch(...) method is linked to be as entrypoint to a
        # middleware. This will be a place where a middleware takes decision
        # to not process request to certain endpoint or not.
        if type(middleware) is Middleware:
            raise TypeError(
                f"cannot accept abstract class implementation {middleware}"
            )
        elif isinstance(middleware, ExceptionHandlerHttpMiddleware):
            self.__register_exception_http_middleware(middleware)
        elif isinstance(middleware, HttpMiddleware):
            self.__register_http_middleware_fn(
                middleware.dispatch
            )
        elif isinstance(middleware, WebsocketMiddleware):
            self.__websocket_stack.add_call(
                DispatchWebsocketHandler(
                    fn=middleware.dispatch
                )
            )
        else:
            raise TypeError(
                f"unrecognized middleware {middleware}"
            )

    def __register_http_middleware_fn(
        self,
        fn: Callable
    ) -> None:
        self.__app._fw_register_middleware(
            StarletteBaseHTTPMiddleware,
            dispatch=fn
        )

    def __register_exception_http_middleware(
        self,
        middleware: ExceptionHandlerHttpMiddleware
    ) -> None:
        # NOTE: It may seem strange that firstly exception handlers are wrapped
        #   into middleware and then unwrapped here for HTTP protocol, but
        #   in this way we comply with other protocols (such as Websocket).
        #   Adding middleware directly as BaseHTTPMiddleware is not an option
        #   since HTTPException (such as 404 Not Found) won't be handled.
        __RemainingExceptionDirectSubclasses: set[type[Exception]] = \
            set(get_exception_direct_subclasses())

        for handler in middleware.handlers:
            __RemainingExceptionDirectSubclasses.discard(
                handler.HandledException
            )

            if handler.HandledException is Exception:
                # Do not add the base exception explicitly since Starlette
                # cannot handle it, add all it's direct subclasses instead
                continue
            else:
                self.__app._fw_register_exception_handler_fn(
                    handler.HandledException,
                    handler.handle
                )

        for Remaining in __RemainingExceptionDirectSubclasses:
            handle_fn: Callable
            if Remaining is HttpException:
                handle_fn = DefaultHttpExceptionHandler().handle
            else:
                # Since ramining exception direct subclasses does not contain
                # Orwynn.Error (see get_exception_direct_subclasses()
                # docstring) we can assign to all rest exceptions a default
                # Exception handler
                handle_fn = DefaultExceptionHandler().handle

            self.__app._fw_register_exception_handler_fn(
                Remaining,
                handle_fn
            )

    def __register_cors_middleware(self) -> None:
        """
        Configures CORS policy used for the whole app.
        """
        if self.__cors is None:
            return
        validation.validate(self.__cors, Cors)

        kwargs: dict[str, Any] = {}
        for k, v in self.__cors.dict().items():
            if v:
                kwargs[k] = v

        self.__app._fw_register_middleware(
            FastAPI_CORSMiddleware,
            **kwargs
        )
