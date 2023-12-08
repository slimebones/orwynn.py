import typing
from typing import Callable

from starlette.types import Receive, Scope, Send

from orwynn.app.config import AppConfig
from orwynn.app.core import CoreApp
from orwynn.app.types import CoreCors
from orwynn.service.framework import FrameworkService
from orwynn.testing import Client, EmbeddedTestClient
from orwynn.url import URLMethod


class App(FrameworkService):
    def __init__(self, config: AppConfig) -> None:
        self._core_app: CoreApp = CoreApp(
            docs_url=config.docs_route,
            redoc_url=config.redoc_route
        )
        self._wrapped_core_app: CoreApp
        if config.cors and config.cors.is_enabled:
            # cors should wrap an application to add required headers to error
            # responses too
            self._wrapped_core_app = typing.cast(
                CoreApp,
                CoreCors(
                    app=self._core_app,
                    allow_origins=config.cors.allow_origins or (),
                    allow_methods=config.cors.allow_methods or ("GET",),
                    allow_headers=config.cors.allow_headers or (),
                    allow_credentials=config.cors.allow_credentials,
                    allow_origin_regex=config.cors.allow_origin_regex,
                    expose_headers=config.cors.expose_headers or (),
                    max_age=config.cors.max_age
                )
            )
        else:
            self._wrapped_core_app = self._core_app

        self._fw_register_middleware = self._core_app.add_middleware
        self._fw_register_exception_handler_fn = \
            self._core_app.add_exception_handler
        self._fw_websocket_handler = self._core_app.websocket

        self.HTTP_METHODS_TO_REGISTERING_FUNCTIONS: \
            dict[URLMethod, Callable] = {
                URLMethod.Get: self._core_app.get,
                URLMethod.Post: self._core_app.post,
                URLMethod.Put: self._core_app.put,
                URLMethod.Delete: self._core_app.delete,
                URLMethod.Patch: self._core_app.patch,
                URLMethod.Options: self._core_app.options
            }

        self._client: Client = Client(
            EmbeddedTestClient(self._wrapped_core_app)
        )

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        await self._wrapped_core_app(scope, receive, send)

    @property
    def core_app(self) -> CoreApp:
        return self._core_app

    @property
    def client(self) -> Client:
        return self._client
