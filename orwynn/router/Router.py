from typing import Any, Callable

from orwynn.app._AlreadyRegisteredMethodError import \
    AlreadyRegisteredMethodError
from orwynn.app._AppService import AppService
from orwynn.base.controller import endpoint
from orwynn.base.worker.Worker import Worker
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

    def register_route_fn(
        self, *, route: str, fn: Callable, method: HTTPMethod
    ) -> None:
        """Registers fn for route.

        Attributes: route:
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
        else:
            try:
                self.__methods_by_route[route].add(method)
            except KeyError:
                self.__methods_by_route[route] = {method}

        spec: endpoint.Spec | None
        try:
            spec = endpoint.SpecsProxy.ie().find_spec(fn)
        except endpoint.SpecNotFoundError:
            spec = None

        app_fn(route, **self.__parse_endpoint_spec_kwargs(spec))(fn)

    def __parse_endpoint_spec_kwargs(
        self, spec: endpoint.Spec | None
    ) -> dict[str, Any]:
        result: dict[str, Any] = {}

        if spec is not None:
            # TODO:
            #   Add response model to framework middleware to call indications.
            #   Others remain as it is.
            result["status_code"] = spec.default_status_code
            result["summary"] = spec.summary
            result["tags"] = spec.tags
            result["response_description"] = spec.response_description
            result["is_deprecated"] = spec.is_deprecated
            result["responses"] = spec.responses

        return result
