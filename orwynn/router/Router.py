import typing
from inspect import isclass
from typing import Any, Callable, Sequence

import pydantic
from fastapi.middleware.cors import CORSMiddleware as FastAPI_CORSMiddleware
from starlette.middleware.base import (
    BaseHTTPMiddleware as StarletteBaseHTTPMiddleware,
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
from orwynn.error.DefaultExceptionHandler import (
    DefaultExceptionHandler,
)
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
        app: App
    ) -> None:
        super().__init__()
        self.__app: App = app
        self.__methods_by_route: dict[str, set[HttpMethod]] = {}
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

    def add_middleware(
        self,
        middleware_arr: Sequence[Middleware],
        *,
        cors: Cors | None
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
        if cors is not None:
            self.__add_cors_middleware(cors)

        # Add HTTP from reversed list to comply Starlette
        for http_middleware in reversed(http_middleware_arr):
            self.__add_middleware(http_middleware)

        # Add Websocket normally
        if websocket_middleware_arr != []:
            if self.__is_websocket_middleware_added:
                raise ValueError(
                    "websocket middleware have been already added"
                )

            for websocket_middleware in websocket_middleware_arr:
                self.__add_middleware(websocket_middleware)

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
        elif isinstance(middleware, ExceptionHandlerHttpMiddleware):
            self.__add_exception_http_middleware(middleware)
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

    def __add_http_middleware_fn(
        self,
        fn: Callable
    ) -> None:
        self.__app._fw_add_middleware(
            StarletteBaseHTTPMiddleware,
            dispatch=fn
        )

    def __add_exception_http_middleware(
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
                self.__app._fw_add_exception_handler_fn(
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

            self.__app._fw_add_exception_handler_fn(
                Remaining,
                handle_fn
            )

    def __add_cors_middleware(self, cors: Cors) -> None:
        """
        Configures CORS policy used for the whole app.
        """
        validation.validate(cors, Cors)

        kwargs: dict[str, Any] = {}
        for k, v in cors.dict().items():
            if v:
                kwargs[k] = v

        self.__app._fw_add_middleware(
            FastAPI_CORSMiddleware,
            **kwargs
        )
