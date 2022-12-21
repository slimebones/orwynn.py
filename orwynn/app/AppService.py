from typing import Any, Callable

from fastapi import FastAPI
from starlette.types import Receive, Scope, Send

from orwynn.app.already_registered_method_error import \
    AlreadyRegisteredMethodError
from orwynn.base.controller.endpoint._Spec import Spec
from orwynn.base.controller.endpoint._SpecNotFoundError import \
    SpecNotFoundError
from orwynn.base.controller.endpoint._SpecsProxy import SpecsProxy
from orwynn.base.service.framework_service import FrameworkService
from orwynn.base.test.TestClient import TestClient
from orwynn.util.http import HTTPMethod
from orwynn.util.http.unsupported_http_method_error import \
    UnsupportedHTTPMethodError


class AppService(FrameworkService):
    def __init__(self) -> None:
        self.__app: FastAPI = FastAPI()

        self._HTTP_METHODS_TO_REGISTERING_FUNCTIONS: \
            dict[HTTPMethod, Callable] = {
                HTTPMethod.GET: self.__app.get,
                HTTPMethod.POST: self.__app.post,
                HTTPMethod.PUT: self.__app.put,
                HTTPMethod.DELETE: self.__app.delete,
                HTTPMethod.PATCH: self.__app.patch,
                HTTPMethod.OPTIONS: self.__app.options
            }

        self._methods_by_route: dict[str, set[HTTPMethod]] = {}

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        await self.__app(scope, receive, send)

    @property
    def test_client(self) -> TestClient:
        return TestClient(self.__app)

    def add_middleware(self) -> None:
        self.__app.middleware

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
        app_fn: Callable | None = \
            self._HTTP_METHODS_TO_REGISTERING_FUNCTIONS.get(
                method, None
            )

        if not app_fn:
            raise UnsupportedHTTPMethodError(
                f"HTTP method {method} is not supported"
            )

        if (
            route in self._methods_by_route.keys()
            and method in self._methods_by_route[route]
        ):
            raise AlreadyRegisteredMethodError(
                f"method {method} has been already registered for route"
                f" \"{route}\""
            )
        else:
            try:
                self._methods_by_route[route].add(method)
            except KeyError:
                self._methods_by_route[route] = {method}

        spec: Spec | None
        try:
            spec = SpecsProxy.ie().find_spec(fn)
        except SpecNotFoundError:
            spec = None

        app_fn(route, **self.__parse_endpoint_spec_kwargs(spec))(fn)

    def __parse_endpoint_spec_kwargs(
        self, spec: Spec | None
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
