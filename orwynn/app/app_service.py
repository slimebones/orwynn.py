from typing import Callable

from fastapi import FastAPI
from starlette.types import Receive, Scope, Send

from orwynn.base.service.framework_service import FrameworkService
from orwynn.base.test.test_client import TestClient
from orwynn.http.http import HTTPMethod
from orwynn.http.unsupported_http_method_error import \
    UnsupportedHTTPMethodError


class AppService(FrameworkService):
    def __init__(self) -> None:
        super().__init__()
        self._app: FastAPI = FastAPI()

        self._HTTP_METHODS_TO_REGISTERING_FUNCTIONS: \
            dict[HTTPMethod, Callable] = {
                HTTPMethod.GET: self._app.get,
                HTTPMethod.POST: self._app.post,
                HTTPMethod.PUT: self._app.put,
                HTTPMethod.DELETE: self._app.delete,
                HTTPMethod.PATCH: self._app.patch,
                HTTPMethod.OPTIONS: self._app.options
            }

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        await self._app(scope, receive, send)

    @property
    def test_client(self) -> TestClient:
        return TestClient(self._app)

    def register_route_fn(
        self, route: str, fn: Callable, method: HTTPMethod
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
        app_fn: Callable | None = \
            self._HTTP_METHODS_TO_REGISTERING_FUNCTIONS.get(
                method, None
            )

        if not app_fn:
            raise UnsupportedHTTPMethodError(
                f"HTTP method {method} is not supported"
            )

        app_fn(route)(fn)
