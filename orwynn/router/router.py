from orwynn.apiversion import ApiVersion
from orwynn.app.app import App
from orwynn.base.controller.controller import Controller
from orwynn.base.errorhandler.errorhandler import ErrorHandler
from orwynn.base.middleware import Middleware
from orwynn.base.module.module import Module
from orwynn.base.worker.worker import Worker
from orwynn.websocket import WebsocketStack

from .register.controller import ControllerRegister
from .register.middleware import MiddlewareRegister


class Router(Worker):
    """
    Manages how the requests and responses flow through the app.
    """
    def __init__(
        self,
        app: App,
        *,
        modules: list[Module],
        controllers: list[Controller],
        middleware_arr: list[Middleware],
        exception_handlers: list[ErrorHandler],
        global_http_route: str,
        global_websocket_route: str,
        api_version: ApiVersion
    ) -> None:
        super().__init__()
        self.__app: App = app

        self.__modules: list[Module] = modules
        self.__controllers: list[Controller] = controllers
        self.__middleware_arr: list[Middleware] = middleware_arr
        self.__exception_handlers: list[ErrorHandler] = exception_handlers

        self.__websocket_stack: WebsocketStack = WebsocketStack(
            self.__app._fw_websocket_handler
        )

        self.__middleware_register: MiddlewareRegister = MiddlewareRegister(
            app=self.__app,
            middleware_arr=self.__middleware_arr,
            exception_handlers=self.__exception_handlers,
            websocket_stack=self.__websocket_stack
        )
        self.__controller_register: ControllerRegister = ControllerRegister(
            app=self.__app,
            modules=self.__modules,
            controllers=self.__controllers,
            websocket_stack=self.__websocket_stack,
            global_http_route=global_http_route,
            global_websocket_route=global_websocket_route,
            api_version=api_version
        )

        self.__start_registering()

    def __start_registering(self) -> None:
        # Register middleware, it should be done before the controller's
        # adding due to the special websocket middleware registering
        self.__middleware_register.register_all()

        # And finally controllers
        self.__controller_register.register_all()

        # After all actions the websocket stack needs to call register action.
        # It is populated during middleware and controller registering.
        self.__websocket_stack.register_all()
