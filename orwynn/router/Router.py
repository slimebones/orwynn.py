import typing
from inspect import isclass
from typing import Any, Callable

import pydantic

from orwynn import validation
from orwynn.app.AlreadyRegisteredMethodError import (
    AlreadyRegisteredMethodError,
)
from orwynn.app.App import App
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.controller.endpoint.EndpointNotFoundError import (
    EndpointNotFoundError,
)
from orwynn.indication.Indication import Indication
from orwynn.model.Model import Model
from orwynn.proxy.BootProxy import BootProxy
from orwynn.proxy.EndpointProxy import EndpointProxy
from orwynn.router.UnmatchedEndpointEntityError import (
    UnmatchedEndpointEntityError,
)
from orwynn.router.WrongHandlerReturnTypeError import (
    WrongHandlerReturnTypeError,
)
from orwynn.web import HTTPMethod
from orwynn.web.UnsupportedHTTPMethodError import UnsupportedHTTPMethodError
from orwynn.worker.Worker import Worker


class Router(Worker):
    """Responsible of ways how request and responses flows through the app."""
    def __init__(
        self,
        app: App
    ) -> None:
        super().__init__()
        self.__app: App = app
        self.__methods_by_route: dict[str, set[HTTPMethod]] = {}

    def register_websocket(
        self, *, route: str, fn: Callable
    ) -> None:
        """Registers websocket for route.

        Attributes:
            route:
                Route to register to.
            fn:
                Function to register.
        """
        validation.validate(route, str)
        validation.validate(fn, Callable)

        self.__app.websocket_handler(route)(fn)

    def register_route(
        self, *, route: str, fn: Callable, method: HTTPMethod
    ) -> None:
        """Registers fn for route.

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
        return any(
            issubclass(typehint, pydantic.BaseModel)
            for typehint in typing.get_type_hints(fn).values()
        )
