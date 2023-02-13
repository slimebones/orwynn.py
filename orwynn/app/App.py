from typing import TYPE_CHECKING, Any, Callable

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware as FastAPI_CORSMiddleware
from starlette.middleware.base import (
    BaseHTTPMiddleware as StarletteBaseHTTPMiddleware,
)
from starlette.types import Receive, Scope, Send

from orwynn import validation
from orwynn.middleware.Middleware import Middleware
from orwynn.service.FrameworkService import FrameworkService
from orwynn.test.Client import Client
from orwynn.test.EmbeddedTestClient import EmbeddedTestClient
from orwynn.web import CORS, HTTPMethod

if TYPE_CHECKING:
    from orwynn.app.ErrorHandler import ErrorHandler


class App(FrameworkService):
    def __init__(self) -> None:
        self.__app: FastAPI = FastAPI(docs_url="/doc")

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
        self.__client: Client = Client(EmbeddedTestClient(self.__app))

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        await self.__app(scope, receive, send)

    @property
    def websocket_handler(self) -> Callable:
        return self.__app.websocket

    @property
    def client(self) -> Client:
        return self.__client

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

    def add_error_handler(self, error_handler: "ErrorHandler") -> None:
        if error_handler.E is None:
            raise TypeError(f"{error_handler} should define class attribute E")

        if isinstance(error_handler.E, list):
            for E in error_handler.E:
                self.__app.add_exception_handler(
                    E,
                    error_handler.handle
                )
        else:
            self.__app.add_exception_handler(
                error_handler.E,
                error_handler.handle
            )
