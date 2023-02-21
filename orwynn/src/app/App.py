from typing import Callable

from starlette.types import Receive, Scope, Send

from orwynn.src.app.CoreApp import CoreApp
from orwynn.src.service.FrameworkService import FrameworkService
from orwynn.src.testing.Client import Client
from orwynn.src.testing.EmbeddedTestClient import EmbeddedTestClient
from orwynn.src.web.http.HttpMethod import HttpMethod


class App(FrameworkService):
    def __init__(self) -> None:
        self.__core_app: CoreApp = CoreApp(docs_url="/doc")

        self._fw_register_middleware = self.__core_app.add_middleware
        self._fw_register_exception_handler_fn = \
            self.__core_app.add_exception_handler

        self.HTTP_METHODS_TO_REGISTERING_FUNCTIONS: \
            dict[HttpMethod, Callable] = {
                HttpMethod.GET: self.__core_app.get,
                HttpMethod.POST: self.__core_app.post,
                HttpMethod.PUT: self.__core_app.put,
                HttpMethod.DELETE: self.__core_app.delete,
                HttpMethod.PATCH: self.__core_app.patch,
                HttpMethod.OPTIONS: self.__core_app.options
            }

        self.__client: Client = Client(EmbeddedTestClient(self.__core_app))

        # Remove FastAPI default exception handlers to not cross with ours -
        # since we write handlers directly via middleware

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
