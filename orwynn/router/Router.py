import typing
from inspect import isclass
from typing import Any, Callable, Literal, Sequence

import pydantic

from orwynn import validation, web
from orwynn.app.AlreadyRegisteredMethodError import (
    AlreadyRegisteredMethodError,
)
from orwynn.app.App import App
from orwynn.boot.api_version.ApiVersion import ApiVersion
from orwynn.controller.Controller import Controller
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.controller.endpoint.EndpointNotFoundError import (
    EndpointNotFoundError,
)
from orwynn.controller.http.HttpController import HttpController
from orwynn.controller.websocket.WebsocketController import WebsocketController
from orwynn.error.DefaultExceptionHandler import (
    DefaultExceptionHandler,
)
from orwynn.error.ExceptionHandler import ExceptionHandler
from orwynn.error.MalfunctionError import MalfunctionError
from orwynn.error.get_exception_direct_subclasses import (
    get_exception_direct_subclasses,
)
from orwynn.error.http.DefaultHttpExceptionHandler import (
    DefaultHttpExceptionHandler,
)
from orwynn.error.http.ExceptionHandlerHttpMiddleware import (
    ExceptionHandlerHttpMiddleware,
)
from orwynn.indication.Indication import Indication
from orwynn.middleware.HttpMiddleware import HttpMiddleware
from orwynn.middleware.Middleware import Middleware
from orwynn.middleware.MiddlewareRegister import MiddlewareRegister
from orwynn.middleware.WebsocketMiddleware import WebsocketMiddleware
from orwynn.model.Model import Model
from orwynn.module.Module import Module
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
from orwynn.web import HttpException, HttpMethod
from orwynn.web.http.Cors import Cors
from orwynn.web.http.UnsupportedHttpMethodError import (
    UnsupportedHttpMethodError,
)
from orwynn.worker.Worker import Worker


class Router(Worker):
    """
    Manages how the requests and responses flow through the app.
    """
    def __init__(
        self,
        app: App,
        *,
        modules: list[Module],
        controllers: list[Controller],
        middleware_arr: list[Middleware],
        exception_handlers: list[ExceptionHandler],
        cors: Cors | None,
        global_http_route: str,
        global_websocket_route: str,
        api_version: ApiVersion
    ) -> None:
        super().__init__()
        self.__app: App = app

        self.__modules: list[Module] = modules
        self.__controllers: list[Controller] = controllers
        self.__middleware_arr: list[Middleware] = middleware_arr
        self.__exception_handlers: list[ExceptionHandler] = exception_handlers

        self.__cors: Cors | None = cors

        self.__global_http_route: str = global_http_route
        self.__global_websocket_route: str = global_websocket_route
        self.__api_version: ApiVersion = api_version

        self.__methods_by_route: dict[str, set[HttpMethod]] = {}
        self.__websocket_stack: WebsocketStack = WebsocketStack(
            self.__app.websocket_handler
        )
        self.__is_websocket_middleware_added: bool = False
        self.__middleware_register: MiddlewareRegister = MiddlewareRegister(
            app=self.__app,
            middleware_arr=self.__middleware_arr,
            exception_handlers=self.__exception_handlers,
            cors=self.__cors,
            websocket_stack=self.__websocket_stack
        )

        self.__start_registering()

    def __start_registering(self) -> None:
        # Register middleware, it should be done before the controller's
        # adding due to the special websocket middleware registering
        self.__middleware_register.register_all()

        # And finally controllers
        self.__register_controllers()

        # After all actions the websocket stack needs to call register action.
        # It is populated during middleware and controller registering.
        self.__websocket_stack.register_all()

    def __add_websocket_controller(
        self, controller: WebsocketController, module_route: str
    ) -> None:
        """Add websocket controller for a route.

        Args:
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
                module_route, controller.route, method_route
            )
            self.__websocket_stack.add_call(
                WebsocketHandler(
                    fn=event_handler.fn,
                    route=final_route
                )
            )

    def __register_http_route(
        self, *, route: str, fn: Callable, method: HttpMethod
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
        validation.validate(method, HttpMethod)

        app_fn: Callable | None = \
            self.__app.HTTP_METHODS_TO_REGISTERING_FUNCTIONS.get(
                method, None
            )

        if not app_fn:
            raise UnsupportedHttpMethodError(
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

    def __register_controllers(
        self
    ) -> None:
        for m in self.__modules:
            for C in m.Controllers:
                self.__register_controller_class_for_module(
                    m, C
                )

    def __register_controller_class_for_module(
        self,
        m: Module,
        C: type[Controller]
    ) -> None:
        if m.route is None:
            raise MalfunctionError(
                f"module {m} has not route and shouldn't have added any"
                " controllers"
            )

        is_controller_found: bool = False
        for c in self.__controllers:
            if type(c) is C:
                is_controller_found = True

                if isinstance(c, HttpController):
                    self.__register_http_controller_for_module(c, m)
                elif isinstance(c, WebsocketController):
                    # Websocket controllers are firstly added and only then
                    # registered to form a correct stack
                    self.__add_websocket_controller(
                        c,
                        module_route=m.route
                    )
                else:
                    raise TypeError(
                        f"controller unsupported type {type(c)}"
                    )
        if not is_controller_found:
            raise MalfunctionError(
                f"no initialized controller found for class {C},"
                f" but it was declared in imported module {m},"
                " so DI should have been initialized it"
            )

    def __register_http_controller_for_module(
        self,
        controller: HttpController,
        module: Module
    ) -> None:
        # At least one method found
        is_method_found: bool = False
        for http_method in HttpMethod:
            # Don't register unused methods
            if http_method in controller.methods:
                is_method_found = True

                routes: set[str] = self.__get_routes_for_http_controller(
                    controller,
                    module
                )

                for route in routes:
                    self.__register_http_route(
                        route=route,
                        fn=controller.get_fn_by_http_method(http_method),
                        method=http_method
                    )

        if not is_method_found:
            raise MalfunctionError(
                f"no http methods found for controller {controller.__class__},"
                " this shouldn't have passed validation at Controller.__init__"
            )

    def __get_routes_for_http_controller(
        self,
        controller: HttpController,
        module: Module
    ) -> set[str]:
        """
        Returns all http routes which given controller accessible from.
        """
        if module.route is None:
            raise MalfunctionError(
                f"module {module} has not route and shouldn't have added any"
                " controllers"
            )

        routes: set[str] = set()
        final_versions: set[int] = set()
        version: int | set[int] | None | Literal["*"] = controller.VERSION

        # Get the latest version if none is specified for controller
        if version is None:
            final_versions.add(self.__api_version.latest)
        elif isinstance(version, int):
            final_versions.add(version)
        elif isinstance(version, set):
            final_versions.update(version)
        elif isinstance(version, str):
            if version != "*":
                raise MalfunctionError(
                    f"version cannot be {version}, a validation check should"
                    " have been performed at HTTPController"
                )
            # Add all supported versions
            final_versions.update(self.__api_version.supported)
        else:
            raise MalfunctionError(
                f"unrecognized version {version}, a validation check should"
                " have been performed at HTTPController"
            )

        for v in final_versions:
            final_global_route: str
            try:
                final_global_route = self.__api_version.apply_version_to_route(
                    self.__global_http_route,
                    v
                )
            except ValueError:
                # No {version} format block
                final_global_route = self.__global_http_route

            # We can concatenate routes such way since routes
            # are validated to not contain following slash
            # -> But join_routes() handles this situation, doesn't it?
            concatenated_route: str = web.join_routes(
                final_global_route,
                module.route,
                controller.route
            )
            routes.add(concatenated_route)

        return routes

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
