from pprint import pprint
import typing
from inspect import isclass
from typing import Any, Callable, Sequence

import pydantic

from starlette.middleware.base import (
    BaseHTTPMiddleware as StarletteBaseHTTPMiddleware,
)
from starlette.middleware.exceptions import (
    ExceptionMiddleware as StarletteExceptionMiddleware
)
from orwynn import validation, web
from orwynn.app.AlreadyRegisteredMethodError import (
    AlreadyRegisteredMethodError,
)
from orwynn.app.App import App
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.controller.endpoint.EndpointNotFoundError import (
    EndpointNotFoundError,
)
from orwynn.controller.websocket.WebsocketController import WebsocketController
from orwynn.error.catching.DefaultHttpExceptionHandler import DefaultHttpExceptionHandler
from orwynn.error.catching.ExceptionHandlerBuiltinHttpMiddleware import ExceptionHandlerBuiltinHttpMiddleware
from orwynn.error.catching.ExceptionHandlerBuiltinWebsocketMiddleware import ExceptionHandlerBuiltinWebsocketMiddleware
from orwynn.error.catching.HandlerByExceptionClass import HandlerByExceptionClass
from orwynn.indication.Indication import Indication
from orwynn.middleware.HttpMiddleware import HttpMiddleware
from orwynn.middleware.Middleware import Middleware
from orwynn.middleware.WebsocketMiddleware import WebsocketMiddleware
from orwynn.model.Model import Model
from orwynn.proxy.BootProxy import BootProxy
from orwynn.proxy.EndpointProxy import EndpointProxy
from orwynn.router.UnmatchedEndpointEntityError import (
    UnmatchedEndpointEntityError,
)
from orwynn.router.WebsocketHandler import (
    DispatchWebsocketHandler,
    WebsocketHandler,
)
from orwynn.router.WebsocketStack import WebsocketStack
from orwynn.router.WrongHandlerReturnTypeError import (
    WrongHandlerReturnTypeError,
)
from orwynn.web import HttpException, HTTPMethod
from orwynn.web.UnsupportedHTTPMethodError import UnsupportedHTTPMethodError
from orwynn.worker.Worker import Worker


class Router(Worker):
    """
    Manages how the requests and responses flow through the app.
    """
    def __init__(
        self,
        app: App
    ) -> None:
        super().__init__()
        self.__app: App = app
        self.__methods_by_route: dict[str, set[HTTPMethod]] = {}
        self.__websocket_stack: WebsocketStack = WebsocketStack(
            self.__app.websocket_handler
        )
        self.__is_websocket_middleware_added: bool = False

    def register_websocket_layers(
        self
    ) -> None:
        """Registers all added websocket instances to the system."""
        self.__websocket_stack.register()

    def add_websocket_controller(
        self, controller: WebsocketController, module_route: str
    ) -> None:
        """Add websocket controller for a route.

        Attributes:
            controller:
                Websocket controller to add.
            module_route:
                Module route to be added to controller's route. It will then be
                joined with method path for each controller's method.
        """
        validation.validate(controller, WebsocketController)
        validation.validate(module_route, str)

        if not self.__is_websocket_middleware_added:
            raise ValueError(
                "add websocket middleware first"
            )

        # Methods started from "on_" or equal to "main" should be registered.
        # "main" is assigned to MODULE_ROUTE + CONTROLLER_ROUTE directly.
        for event_handler in controller.event_handlers:
            method_route: str = \
                "/" if event_handler.name == "main" else event_handler.name
            final_route: str = web.join_routes(
                controller.route, module_route, method_route
            )
            self.__websocket_stack.add_call(
                WebsocketHandler(
                    fn=event_handler.fn,
                    route=final_route
                )
            )


    def register_route(
        self, *, route: str, fn: Callable, method: HTTPMethod
    ) -> None:
        """Registers a fn for a route.

        Attributes:
            route:
                Route to register to.
            fn:
                Function to register.
            method:
                HTTP method function is handling.
        """
        validation.validate(route, str)
        validation.validate(fn, Callable)
        validation.validate(method, HTTPMethod)

        app_fn: Callable | None = \
            self.__app.HTTP_METHODS_TO_REGISTERING_FUNCTIONS.get(
                method, None
            )

        if not app_fn:
            raise UnsupportedHTTPMethodError(
                f"HTTP method {method} is not supported"
            )

        if (
            route in self.__methods_by_route
            and method in self.__methods_by_route[route]
        ):
            raise AlreadyRegisteredMethodError(
                f"method {method} has been already registered for route"
                f" \"{route}\""
            )

        try:
            self.__methods_by_route[route].add(method)
        except KeyError:
            self.__methods_by_route[route] = {method}

        spec: Endpoint | None
        try:
            spec = EndpointProxy.ie().find_spec(fn)
        except EndpointNotFoundError:
            spec = None

        app_fn(
            route,
            **self.__parse_endpoint_spec_kwargs(
                spec,
                fn
            )
        )(fn)

    def add_middleware(self, middleware: Sequence[Middleware]) -> None:
        """
        Adds middleware to the system.
        """
        # Note that middleware here is reversed since Starlette.add_middleware
        # inserts new functions at the top of the middleware list which makes
        # older added middlewares executable last, which is not logical.
        #
        # But this reversion should be executed only for HtppMiddleware since
        # for Websockets we have own logic.
        #
        # So, first task is to separate middleware
        http_middleware: list[HttpMiddleware] = []
        websocket_middleware: list[WebsocketMiddleware] = []

        for middleware_ in middleware:
            if isinstance(middleware_, HttpMiddleware):
                http_middleware.append(middleware_)
            elif isinstance(middleware_, WebsocketMiddleware):
                websocket_middleware.append(middleware_)
            elif type(middleware_) is Middleware:
                raise TypeError(
                    f"cannot register an instance {middleware_} of an abstact"
                    " class Middleware"
                )
            else:
                raise TypeError(
                    f"unrecognized middleware {middleware_}"
                )

        # Add HTTP from reversed list to comply Starlette
        for http_middleware_ in reversed(http_middleware):
            self.__add_middleware(http_middleware_)

        # Add Websocket normally
        if websocket_middleware != []:
            if self.__is_websocket_middleware_added:
                raise ValueError(
                    "websocket middleware have been already added"
                )

            for websocket_middleware_ in websocket_middleware:
                self.__add_middleware(websocket_middleware_)

            self.__is_websocket_middleware_added = True

    def __add_middleware(self, middleware: Middleware) -> None:
        validation.validate(middleware, Middleware)

        # Note that dispatch(...) method is linked to be as entrypoint to a
        # middleware. This will be a place where a middleware takes decision
        # to not process request to certain endpoint or not.
        if type(middleware) is Middleware:
            raise TypeError(
                f"cannot accept abstract class implementation {middleware}"
            )
        elif isinstance(middleware, HttpMiddleware):
            self.__add_http_middleware_fn(
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

    def __parse_endpoint_spec_kwargs(
        self, spec: Endpoint | None, fn: Callable
    ) -> dict[str, Any]:
        result: dict[str, Any] = {}
        fn_return_typehint: Any | None = typing.get_type_hints(fn).get(
            "return", None
        )

        if spec is not None:
            result["status_code"] = spec.default_status_code
            result["summary"] = spec.summary
            result["tags"] = spec.tags
            result["deprecated"] = spec.is_deprecated

            api_indication: Indication = BootProxy.ie().api_indication
            final_responses: dict[int, dict[str, Any]] = {}
            if spec.responses:
                for response in spec.responses:
                    if (
                        response.status_code == spec.default_status_code
                        and response.Entity is not fn_return_typehint
                    ):
                        raise UnmatchedEndpointEntityError(
                            f"route handler {fn} response endpoint entity"
                            f" {response.Entity} is not match returned"
                            f" typehint {fn_return_typehint}"
                        )

                    final_responses[response.status_code] = {
                        "model": api_indication.gen_schema(response.Entity),
                        "description": response.description
                    }

            # Add default status code response AKA response_model
            if spec.default_status_code not in final_responses:
                if (
                    fn_return_typehint is not None
                    and isclass(fn_return_typehint)
                    and issubclass(fn_return_typehint, Model)
                ):
                    final_responses[spec.default_status_code] = {
                        "model": api_indication.gen_schema(
                            fn_return_typehint
                        )
                    }
                elif fn_return_typehint not in [dict, None]:
                    raise WrongHandlerReturnTypeError(
                        f"route handler {fn} should have either Model, dict"
                        f" or None return type, got {fn_return_typehint}"
                        " instead"
                    )
                else:
                    result["response_model"] = None

            # Add default pydantic validation error
            if (
                422 not in final_responses
                and self.__is_pydantic_validation_error_can_occur_in_fn(fn)
            ):
                final_responses[422] = {
                    "model": api_indication.gen_schema(
                        pydantic.ValidationError
                    ),
                    "description": "Validation Error"
                }
            result["responses"] = final_responses

        return result

    def __is_pydantic_validation_error_can_occur_in_fn(
        self,
        fn: Callable
    ) -> bool:
        # Wrap return statement in try...except to prevent error from
        # issubclass() about wrong typehint (typehint is not a class)
        for typehint in typing.get_type_hints(fn).values():
            try:
                flag: bool = issubclass(typehint, pydantic.BaseModel)
            except TypeError:
                continue
            else:
                if flag:
                    return True
        return False

    def add_http_exception_handlers(
        self,
        handler_by_exception_class: HandlerByExceptionClass,
    ) -> None:
        prepared_handlers: dict[type[Exception], Callable] = {}

        for Exc_, handler in handler_by_exception_class.items():
            prepared_handlers[Exc_] = handler.handle

        self.__app._fw_add_middleware(
            # Add base http middleware with upstream handling instead of
            # starlette's ExceptionMiddleware (since some problems occured with
            # the last option)
            StarletteBaseHTTPMiddleware,
            dispatch=ExceptionHandlerBuiltinHttpMiddleware(
                handlers=set(handler_by_exception_class.values())
            ).dispatch
        )

    def add_websocket_exception_handlers(
        self,
        handler_by_exception_class: HandlerByExceptionClass,
    ) -> None:
        self.__websocket_stack.add_call(
            DispatchWebsocketHandler(
                fn=ExceptionHandlerBuiltinWebsocketMiddleware(
                    handlers=set(handler_by_exception_class.values())
                ).dispatch
            )
        )

    def __add_http_middleware_fn(
        self,
        fn: Callable
    ) -> None:
        self.__app._fw_add_middleware(
            StarletteBaseHTTPMiddleware,
            dispatch=fn
        )
