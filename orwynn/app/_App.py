from typing import Callable

from starlette.types import Receive, Scope, Send

from orwynn.app._AppConfig import AppConfig
from orwynn.app._CoreApp import CoreApp
from orwynn.base.service._FrameworkService import FrameworkService
from orwynn.helpers.web import RequestMethod
from orwynn.testing import Client, EmbeddedTestClient


class App(FrameworkService):
    def __init__(self, config: AppConfig) -> None:
        self.__core_app: CoreApp = CoreApp(
            docs_url=config.docs_route,
            redoc_url=config.redoc_route
        )

        self._fw_register_middleware = self.__core_app.add_middleware
        self._fw_register_exception_handler_fn = \
            self.__core_app.add_exception_handler
        self._fw_websocket_handler = self.__core_app.websocket

        self.HTTP_METHODS_TO_REGISTERING_FUNCTIONS: \
            dict[RequestMethod, Callable] = {
                RequestMethod.GET: self.__core_app.get,
                RequestMethod.POST: self.__core_app.post,
                RequestMethod.PUT: self.__core_app.put,
                RequestMethod.DELETE: self.__core_app.delete,
                RequestMethod.PATCH: self.__core_app.patch,
                RequestMethod.OPTIONS: self.__core_app.options
            }

        self.__client: Client = Client(EmbeddedTestClient(self.__core_app))

        # Remove FastAPI default exception handlers to not cross with ours -
        # since we write handlers directly via middleware

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        await self.__core_app(scope, receive, send)

    @property
    def client(self) -> Client:
        return self.__client
