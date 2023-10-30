import typing
from inspect import isclass
from typing import Any, Callable, Literal

import pydantic

from orwynn.apiversion import ApiVersion
from orwynn.app import App
from orwynn.base.controller.controller import Controller
from orwynn.base.controller.errors import AlreadyRegisteredMethodError
from orwynn.base.error import MalfunctionError
from orwynn.base.model import Model
from orwynn.base.module import Module
from orwynn.helpers.web import REQUEST_METHOD_BY_PROTOCOL, RequestMethod
from orwynn.http import Endpoint, EndpointContainer, HttpController
from orwynn.http.errors import (
    EndpointNotFoundError,
    UnsupportedHttpMethodError,
)
from orwynn.indication.indication import Indication
from orwynn.proxy.boot import BootProxy
from orwynn.router.errors import (
    UnmatchedEndpointEntityError,
)
from orwynn.utils import validation
from orwynn.utils.scheme import Scheme
from orwynn.utils.url import join_routes
from orwynn.websocket import (
    WebsocketController,
    WebsocketStack,
    routing_handlers,
)


class ControllerRegister:
    """
    Registers controllers to the system.
    """
    def __init__(
        self,
        *,
        app: App,
        modules: list[Module],
        controllers: list[Controller],
        websocket_stack: WebsocketStack,
        global_http_route: str,
        global_websocket_route: str,
        api_version: ApiVersion
    ) -> None:
        self.__app: App = app

        self.__modules: list[Module] = modules
        self.__controllers: list[Controller] = controllers
        self.__methods_by_route: dict[str, set[RequestMethod]] = {}

        self.__global_http_route: str = global_http_route
        self.__global_websocket_route: str = global_websocket_route
        self.__api_version: ApiVersion = api_version

        self.__websocket_stack: WebsocketStack = websocket_stack

    def register_all(
        self
    ) -> None:
        """
        Registers all controllers to the system.
        """
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
                    self.__add_websocket_controller_for_module(
                        c,
                        m
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

    def __add_websocket_controller_for_module(
        self, controller: WebsocketController, module: Module
    ) -> None:
        """Add websocket controller for a route.

        Args:
            controller:
                Websocket controller to add.
            module:
                Module to register for.
        """
        # Methods started from "on_" or equal to "main" should be registered.
        # "main" is assigned to MODULE_Route + CONTROLLER_Route directly.
        for event_handler in controller.event_handlers:
            method_route: str = \
                "/" if event_handler.name == "main" else event_handler.name
            routes: set[str] = self.__get_routes_for_controller(
                controller,
                module,
                additional_route=method_route
            )

            controller._fw_update_final_routes(routes)

            for route in routes:
                self.__websocket_stack.add_call(
                    routing_handlers.WebsocketHandler(
                        fn=event_handler.fn,
                        route=route
                    )
                )

    def __register_http_controller_for_module(
        self,
        controller: HttpController,
        module: Module
    ) -> None:
        routes: set[str] = self.__get_routes_for_controller(
            controller,
            module
        )

        # At least one method found
        is_method_found: bool = False
        for http_method in RequestMethod:
            # Don't register unused methods
            if (
                http_method in controller.methods
                and http_method in REQUEST_METHOD_BY_PROTOCOL[Scheme.HTTP]
            ):
                is_method_found = True

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
        else:
            # Make the controller know about it's full routes
            controller._fw_update_final_routes(routes)

    def __get_routes_for_controller(
        self,
        controller: Controller,
        module: Module,
        *,
        additional_route: str = ""
    ) -> set[str]:
        """
        Returns all routes which given controller accessible from.

        Args:
            ...
            additional_route (optional):
                Route to append addiotionally to the end of normally
                concatenated route. Defaults to empty string.
        """
        if module.route is None:
            raise MalfunctionError(
                f"module {module} has not route and shouldn't have added any"
                " controllers"
            )

        routes: set[str] = set()
        final_versions: set[int] = set()
        version: int | set[int] | None | Literal["*"] = controller.Version

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
            final_global_route: str = self.__get_global_route_for_controller(
                controller,
                api_version_number=v
            )

            concatenated_route: str
            if isinstance(controller, HttpController):
                # We can concatenate routes such way since routes
                # are validated to not contain following slash
                # -> But join_routes() handles this situation, doesn't it?
                concatenated_route = join_routes(
                    final_global_route,
                    module.route,
                    controller.route,
                    additional_route
                )
            elif isinstance(controller, WebsocketController):
                concatenated_route = join_routes(
                    final_global_route,
                    module.route,
                    controller.route,
                    additional_route
                )
            else:
                raise TypeError(
                    f"unrecognized controller {controller}"
                )
            routes.add(concatenated_route)

        return routes

    def __get_global_route_for_controller(
        self,
        controller: Controller,
        *,
        api_version_number: int
    ) -> str:
        # Choose which protocol's global route to use
        global_route: str
        if isinstance(controller, HttpController):
            global_route = self.__global_http_route
        elif isinstance(controller, WebsocketController):
            global_route = self.__global_websocket_route
        else:
            raise TypeError(
                f"unrecognized controller {controller}"
            )

        try:
            return self.__api_version.apply_version_to_route(
                global_route,
                api_version_number
            )
        except ValueError:
            # No {version} format block
            return global_route

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
                        and fn_return_typehint is not dict
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

    def __register_http_route(
        self, *, route: str, fn: Callable, method: RequestMethod
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
        validation.validate(method, RequestMethod)

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
            spec = EndpointContainer.ie().find_spec(fn)
        except EndpointNotFoundError:
            spec = None

        app_fn(
            route,
            **self.__parse_endpoint_spec_kwargs(
                spec,
                fn
            )
        )(fn)
