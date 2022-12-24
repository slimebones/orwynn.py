import typing
from inspect import isclass
from typing import Any, Callable

import pydantic

from orwynn.app.AlreadyRegisteredMethodError import \
    AlreadyRegisteredMethodError
from orwynn.app.AppService import AppService
from orwynn.base.controller.endpoint.Endpoint import Endpoint
from orwynn.base.controller.endpoint.EndpointNotFoundError import \
    EndpointNotFoundError
from orwynn.base.indication.Indication import Indication
from orwynn.base.model.Model import Model
from orwynn.base.worker._Worker import Worker
from orwynn.proxy.BootProxy import BootProxy
from orwynn.proxy.EndpointProxy import EndpointProxy
from orwynn.util import validation
from orwynn.util.web import HTTPMethod
from orwynn.util.web.UnsupportedHTTPMethodError import \
    UnsupportedHTTPMethodError


class Router(Worker):
    """Responsible of ways how request and responses flows through the app."""
    def __init__(
        self,
        app: AppService
    ) -> None:
        super().__init__()
        self.__app: AppService = app
        self.__methods_by_route: dict[str, set[HTTPMethod]] = {}

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
            route in self.__methods_by_route.keys()
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
            # TODO:
            #   Add response model to framework middleware to call indications.
            #   Others remain as it is.
            if fn_return_typehint is None:
                result["response_model"] = spec.ResponseModel
            elif not isclass(fn_return_typehint):
                raise TypeError(
                    "fn return typehint should be a Class or None,"
                    f" {fn_return_typehint} got instead"
                )
            elif (
                not issubclass(fn_return_typehint, Model)
                and not issubclass(fn_return_typehint, dict)
                and fn_return_typehint is not typing.Any
            ):
                raise TypeError(
                    f"endpoint shouldn't return {fn_return_typehint}"
                )
            elif (
                spec.ResponseModel is None
                and issubclass(fn_return_typehint, Model)
            ):
                result["response_model"] = fn_return_typehint
            else:
                result["response_model"] = spec.ResponseModel

            result["status_code"] = spec.default_status_code
            result["summary"] = spec.summary
            result["tags"] = spec.tags
            result["response_description"] = spec.response_description
            result["deprecated"] = spec.is_deprecated

            api_indication: Indication = BootProxy.ie().api_indication
            final_responses: dict[int, dict[str, Any]] = {}
            if spec.responses:
                for response in spec.responses:
                    final_responses[response.status_code] = {
                        "model": api_indication.gen_schema(response.Entity)
                    }
            # Add default pydantic validation error
            if (
                414 not in final_responses
                and self.__is_pydantic_validation_error_can_occur_in_fn(fn)
            ):
                final_responses[414] = {
                    "model": api_indication.gen_schema(
                        pydantic.ValidationError
                    )
                }
            result["responses"] = final_responses

        return result

    def __is_pydantic_validation_error_can_occur_in_fn(
        self,
        fn: Callable
    ) -> bool:
        for typehint in typing.get_type_hints(fn).values():
            # Check pydantic base models in case user used them instead of
            # orwynn.Model
            if issubclass(typehint, pydantic.BaseModel):
                return True
        return False
