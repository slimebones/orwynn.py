from typing import TYPE_CHECKING, Any, Awaitable, Callable, Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware as FastAPI_CORSMiddleware
from orwynn import web
from orwynn.error.catching.ErrorHandlerBuiltinHttpMiddleware import ErrorHandlerBuiltinHttpMiddleware
from starlette.middleware.base import (
    BaseHTTPMiddleware as StarletteBaseHTTPMiddleware,
)
from starlette.middleware.exceptions import (
    ExceptionMiddleware as StarletteExceptionMiddleware
)
from starlette.types import Receive, Scope, Send

from orwynn import validation
from orwynn.error.catching.DefaultExceptionHandler import DefaultExceptionHandler
from orwynn.service.FrameworkService import FrameworkService
from orwynn.testing.Client import Client
from orwynn.testing.EmbeddedTestClient import EmbeddedTestClient
from orwynn.validation.RequestValidationException import RequestValidationException
from orwynn.web import CORS, HTTPMethod, Response

if TYPE_CHECKING:
    pass


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

    def add_http_middleware_fn(
        self,
        fn: Callable
    ) -> None:
        self.__app.add_middleware(
            StarletteBaseHTTPMiddleware,
            dispatch=fn
        )

    def add_http_exception_middleware_fn(
        self,
        HandledException: type[Exception]
        fn: Callable[[web.Request, Exception], web.Response]
    ) -> None:
        self.__app.add_middleware(
            StarletteExceptionMiddleware,
            handlers={HandledException: DefaultExceptionHandler().handle}
        )
