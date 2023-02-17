from typing import TYPE_CHECKING, Any, Awaitable, Callable, Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware as FastAPI_CORSMiddleware
from starlette.types import Receive, Scope, Send

from orwynn import validation, web
from orwynn.app.CoreApp import CoreApp
from orwynn.error.catching.DefaultHttpExceptionHandler import DefaultHttpExceptionHandler
from orwynn.service.FrameworkService import FrameworkService
from orwynn.testing.Client import Client
from orwynn.testing.EmbeddedTestClient import EmbeddedTestClient
from orwynn.validation.RequestValidationException import \
    RequestValidationException
from orwynn.web import CORS, HttpException, HTTPMethod


class App(FrameworkService):
    def __init__(self) -> None:
        self.__core_app: CoreApp = CoreApp(docs_url="/doc")

        self._fw_add_middleware = self.__core_app.add_middleware

        self.HTTP_METHODS_TO_REGISTERING_FUNCTIONS: \
            dict[HTTPMethod, Callable] = {
                HTTPMethod.GET: self.__core_app.get,
                HTTPMethod.POST: self.__core_app.post,
                HTTPMethod.PUT: self.__core_app.put,
                HTTPMethod.DELETE: self.__core_app.delete,
                HTTPMethod.PATCH: self.__core_app.patch,
                HTTPMethod.OPTIONS: self.__core_app.options
            }

        self.__is_cors_configured: bool = False
        self.__client: Client = Client(EmbeddedTestClient(self.__core_app))

        # Remove FastAPI default exception handlers to not cross with ours -
        # since we write handlers directly via middleware
        del self.__core_app.exception_handlers[HttpException]
        del self.__core_app.exception_handlers[RequestValidationException]

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        await self.__core_app(scope, receive, send)

    @property
    def websocket_handler(self) -> Callable:
        return self.__core_app.websocket

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

        self.__core_app.add_middleware(
            FastAPI_CORSMiddleware,
            **kwargs
        )
        self.__is_cors_configured = True
