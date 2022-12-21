from typing import Any, Callable
from fastapi import FastAPI
from starlette.types import Receive, Scope, Send
from orwynn.base.middleware._Middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware \
    as StarletteBaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware as FastAPI_CORSMiddleware

from orwynn.base.service.framework_service import FrameworkService
from orwynn.base.test.HttpClient import HttpClient
from orwynn.base.test.TestClient import TestClient
from orwynn.util import validation
from orwynn.util.web import CORS, HTTPMethod


class AppService(FrameworkService):
    def __init__(self) -> None:
        self.__app: FastAPI = FastAPI()

        self.HTTP_METHODS_TO_REGISTERING_FUNCTIONS: \
            dict[HTTPMethod, Callable] = {
                HTTPMethod.GET: self.__app.get,
                HTTPMethod.POST: self.__app.post,
                HTTPMethod.PUT: self.__app.put,
                HTTPMethod.DELETE: self.__app.delete,
                HTTPMethod.PATCH: self.__app.patch,
                HTTPMethod.OPTIONS: self.__app.options
            }

        self.__is_cors_configured: bool = False

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        await self.__app(scope, receive, send)

    @property
    def test_client(self) -> TestClient:
        return TestClient(self.__app)

    @property
    def http_client(self) -> HttpClient:
        return HttpClient(self.test_client)

    def add_middleware(self, middleware: Middleware) -> None:
        validation.validate(middleware, Middleware)
        # Note that dispatch(...) method is linked to be as entrypoint to
        # middleware. This will be a place where a middleware takes decision
        # to not process request to certain endpoint or not.
        self.__app.add_middleware(
            StarletteBaseHTTPMiddleware,
            dispatch=middleware.dispatch
        )

    def configure_cors(self, cors: CORS) -> None:
        """Configures CORS policy used for the whole app."""
        if self.__is_cors_configured:
            raise ValueError("CORS has been already configured")

        validation.validate(cors, CORS)

        kwargs: dict[str, Any] = {}
        for k, v in cors.dict().items():
            if v:
                kwargs[k] = v

        self.__app.add_middleware(
            FastAPI_CORSMiddleware,
            **kwargs
        )
        self.__is_cors_configured = True
