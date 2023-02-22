import os
from copy import deepcopy
from pathlib import Path
from types import NoneType

import dotenv

from orwynn.src import validation
from orwynn.src.app.App import App
from orwynn.src.apprc.AppRc import AppRc
from orwynn.src.apprc.parse_apprc import parse_apprc
from orwynn.src.boot.api_version.ApiVersion import ApiVersion
from orwynn.src.boot.BootMode import BootMode
from orwynn.src.controller.Controller import Controller
from orwynn.src.di.Di import Di
from orwynn.src.di.MissingDiObjectError import MissingDiObjectError
from orwynn.src.error.ExceptionHandler import ExceptionHandler
from orwynn.src.file.NotDirError import NotDirError
from orwynn.src.indication.default_api_indication import default_api_indication
from orwynn.src.indication.Indication import Indication
from orwynn.src.log.configure_log import configure_log
from orwynn.src.log.LogConfig import LogConfig
from orwynn.src.middleware.GlobalMiddlewareSetup import GlobalMiddlewareSetup
from orwynn.src.middleware.Middleware import Middleware
from orwynn.src.module.Module import Module
from orwynn.src.proxy.APIIndicationOnlyProxy import APIIndicationOnlyProxy
from orwynn.src.proxy.BootProxy import BootProxy
from orwynn.src.proxy.EndpointProxy import EndpointProxy
from orwynn.src.router.Router import Router
from orwynn.src.testing.Client import Client
from orwynn.src.validation import (
    validate,
    validate_dict,
    validate_each,
)
from orwynn.src.web.http.Cors import Cors
from orwynn.src.worker.Worker import Worker


class Boot(Worker):
    """Worker responsible of booting an application.

    General usage is to construct this class in the main.py with required
    parameters and then access Boot.app for your needs.

    Attributes:
        root_module:
            Root module of the app.
        dotenv_path (optional):
            Path to .env file. Defaults to ".env".
        api_indication (optional):
            Indication object used as a convention for outcoming API
            structures. Defaults to predefined by framework's indication
            convention.
        cors (optional):
            CORS policy applied to the whole application. No CORS applied by
            default.
        ExceptionHandlers (optional):
            List of exception handlers to add. By default framework adds
            the builtin Exception and orwynn.Error handlers.
        apprc (optional):
            Application configuration. By default environ Orwynn_AppRcPath is
            checked if this arg is not given.
        mode (optional):
            Application mode. By default environ Orwynn_Mode is
            checked if this arg is not given.
        global_http_route (optional):
            Global route to be prepended to every controller's route. Defaults
            to no route. Can accept formatting "{version}" for an API version
            to be injected into route.
        global_websocket_route (optional):
            Global route to be prepended to every controller's route. Defaults
            to no route. Can accept formatting "{version}" for an API version
            to be injected into route.
        global_imports (optional):
            Modules available across all other modules imported into the
            application. Note that no other instance can import a globally
            available module.
        global_middleware (optional):
            Map of middleware and its covered routes to apply globally. Note
            that every initialized Provider can be accessed from such
            middleware.
        api_version (optional):
            Object describes API versioning rules for the project. By default
            only v1 is supported.

    Environs:
        Orwynn_Mode:
            Boot mode for application. Defaults to DEV. Alternatively you can
            pass arg "mode".
        Orwynn_RootDir:
            Root directory for application. Defaults to os.getcwd()
        Orwynn_AppRcPath:
            Path where app configuration file located. Defaults to
            "./apprc.yml". Alternatively you can pass a dictionary directly in
            "apprc" attribute.

    Usage:
    ```py
    # main.py
    from orwynn import Boot, App

    # Import root module from your location
    from .myproject.root_module import root_module

    app: App = Boot(
        root_module=root_module
    ).app
    ```
    """
    def __init__(
        self,
        root_module: Module,
        *,
        dotenv_path: Path | None = None,
        api_indication: Indication | None = None,
        cors: Cors | None = None,
        ExceptionHandlers: set[type[ExceptionHandler]] | None = None,
        apprc: AppRc | None = None,
        mode: BootMode | None = None,
        global_http_route: str | None = None,
        global_websocket_route: str | None = None,
        global_modules: list[Module] | None = None,
        global_middleware: GlobalMiddlewareSetup | None = None,
        api_version: ApiVersion | None = None
    ) -> None:
        super().__init__()
        if dotenv_path is None:
            dotenv_path = Path(".env")
        validate(dotenv_path, Path)
        validate(root_module, Module)
        if api_indication is None:
            api_indication = default_api_indication
        validate(api_indication, Indication)
        validate(cors, [Cors, NoneType])
        if ExceptionHandlers is None:
            ExceptionHandlers = set()
        validate_each(
            ExceptionHandlers, ExceptionHandler, expected_sequence_type=set
        )
        validate(apprc, [AppRc, NoneType])
        validate(mode, [BootMode, NoneType])

        if global_http_route is None:
            global_http_route = ""
        validate(global_http_route, str)

        if global_websocket_route is None:
            global_websocket_route = ""
        validate(global_websocket_route, str)

        if global_modules is None:
            global_modules = []
        validate_each(global_modules, Module, expected_sequence_type=list)

        if global_middleware is None:
            global_middleware = {}
        validate_dict(
            global_middleware, (Middleware, list)
        )

        if api_version is None:
            api_version = ApiVersion()
        validate(api_version, ApiVersion)

        dotenv.load_dotenv(dotenv_path, override=True)

        self.__mode: BootMode
        if mode:
            self.__mode = mode
        else:
            self.__mode = self.__parse_mode()
        self.__root_dir: Path = self.__parse_root_dir()
        self.__api_indication: Indication = api_indication
        self.__apprc: AppRc = parse_apprc(
            self.__root_dir,
            self.__mode,
            deepcopy(apprc)
        )
        self.__global_http_route: str = global_http_route
        self.__global_websocket_route: str = global_websocket_route
        self.__api_version: ApiVersion = api_version

        # Init proxies
        BootProxy(
            root_dir=self.__root_dir,
            mode=self.__mode,
            api_indication=self.__api_indication,
            apprc=self.__apprc,
            ExceptionHandlers=ExceptionHandlers,
            global_http_route=self.__global_http_route,
            global_websocket_route=self.__global_websocket_route,
            api_version=self.__api_version
        )
        EndpointProxy()
        APIIndicationOnlyProxy(api_indication)
        ##

        # Add framework services
        root_module._fw_add_provider_or_skip(App)
        # Log config is always added to configure logging, it can be built from
        # an empty apprc too.
        root_module._fw_add_provider_or_skip(LogConfig)
        ##

        self.__di: Di = Di(
            root_module,
            global_modules=global_modules,
            global_middleware=global_middleware
        )

        # Configure logging
        configure_log(validation.apply(self.__di.find("LogConfig"), LogConfig))

        self.__router: Router = self.__init_router(
            cors=cors
        )

    def __init_router(
        self,
        *,
        cors: Cors | None
    ) -> Router:
        try:
            all_modules: list[Module] = self.__di.modules
        except MissingDiObjectError:
            all_modules = []

        try:
            all_controllers: list[Controller] = self.__di.controllers
        except MissingDiObjectError:
            all_controllers = []

        try:
            all_middleware: list[Middleware] = self.__di.all_middleware
        except MissingDiObjectError:
            all_middleware = []

        try:
            all_exception_handlers: list[ExceptionHandler] = \
                self.__di.exception_handlers
        except MissingDiObjectError:
            all_exception_handlers = []

        return Router(
            self.app,
            global_http_route=self.__global_http_route,
            global_websocket_route=self.__global_websocket_route,
            api_version=self.__api_version,
            cors=cors,
            modules=all_modules,
            controllers=all_controllers,
            middleware_arr=all_middleware,
            exception_handlers=all_exception_handlers
        )

    @property
    def app(self) -> App:
        return self.__di.app_service

    @property
    def client(self) -> Client:
        """
        Convenience shortcut to get testing client from the App.
        """
        return self.app.client

    @property
    def mode(self) -> BootMode:
        return self.__mode

    @property
    def api_indication(self) -> Indication:
        return self.__api_indication

    def __parse_mode(self) -> BootMode:
        mode_env: str | None = os.getenv("Orwynn_Mode")

        if not mode_env:
            return BootMode.DEV
        else:
            return BootMode(mode_env)

    def __parse_root_dir(self) -> Path:
        root_dir: Path
        root_dir_env: str = os.getenv("Orwynn_RootDir", "")

        root_dir = \
            Path(os.getcwd()) if not root_dir_env else Path(root_dir_env)

        if not root_dir.is_dir():
            raise NotDirError(
                f"{root_dir} is not a directory"
            )

        return root_dir
