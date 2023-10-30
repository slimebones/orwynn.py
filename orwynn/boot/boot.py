import contextlib
import os
from copy import deepcopy
from pathlib import Path
from types import NoneType
from typing import Self

import dotenv
from starlette.types import Receive, Scope, Send

from orwynn.apiversion import ApiVersion
from orwynn.app import App, AppMode
from orwynn.apprc import AppRc, AppRCUtils
from orwynn.base.controller import Controller
from orwynn.base.errorhandler import ErrorHandler
from orwynn.base.middleware import GlobalMiddlewareSetup, Middleware
from orwynn.base.module import Module
from orwynn.base.worker import Worker
from orwynn.bootscript import Bootscript, BootscriptWorker, CallTime
from orwynn.bootscript.errors import NoScriptsForCallTimeError
from orwynn.di.di import Di
from orwynn.di.errors import MissingDiObjectError
from orwynn.helpers.errors import DeprecatedFeatureError
from orwynn.http import EndpointContainer
from orwynn.indication import Indication, default_api_indication
from orwynn.log import LogConfig, LogUtils
from orwynn.proxy.boot import BootProxy
from orwynn.proxy.indicationonly import ApiIndicationOnlyProxy
from orwynn.router import Router
from orwynn.testing import Client
from orwynn.utils import validation
from orwynn.utils.validation import validate, validate_dict, validate_each
from orwynn.utils.yml.errors import NotDirError


class Boot(Worker):
    """Worker responsible of booting an application.

    General usage is to construct this class in the main.py with required
    parameters and then access Boot.app for your needs.

    Environs:
        - ORWYNN_MODE:
            Boot mode for application. Defaults to DEV. Alternatively you can
            pass arg "mode".
        - ORWYNN_ROOT_DIR:
            Root directory for application. Defaults to os.getcwd()
        - ORWYNN_RC_PATH:
            Path where app configuration file located. Defaults to
            "./apprc.yml". Alternatively you can pass a dictionary directly in
            "apprc" attribute.
    """
    def __init__(
        self,
        root_module: Module,
        *,
        dotenv_path: Path | None = None,
        api_indication: Indication | None = None,
        ErrorHandlers: set[type[ErrorHandler]] | None = None,
        apprc: AppRc | None = None,
        mode: AppMode | None = None,
        global_http_route: str | None = None,
        global_websocket_route: str | None = None,
        global_modules: list[Module] | None = None,
        global_middleware: GlobalMiddlewareSetup | None = None,
        api_version: ApiVersion | None = None,
        bootscripts: list[Bootscript] | None = None,
        _fw_init_lock: bool = True
    ) -> None:
        self._check_init_lock(_fw_init_lock)

        if dotenv_path is None:
            dotenv_path = Path(".env")
        validate(dotenv_path, Path)
        validate(root_module, Module)
        if api_indication is None:
            api_indication = default_api_indication
        validate(api_indication, Indication)
        if ErrorHandlers is None:
            ErrorHandlers = set()
        validate_each(
            ErrorHandlers, ErrorHandler, expected_sequence_type=set
        )
        validate(apprc, [AppRc, NoneType])
        validate(mode, [AppMode, NoneType])

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

        if bootscripts is None:
            bootscripts = []
        validate_each(
            bootscripts,
            Bootscript,
            expected_sequence_type=list
        )

        dotenv.load_dotenv(dotenv_path, override=True)

        self.__mode: AppMode = self.__initialize_mode(mode)
        self.__root_dir: Path = self.__parse_root_dir()
        self.__api_indication: Indication = api_indication
        self.__apprc: AppRc = AppRCUtils.parse(
            self.__root_dir,
            self.__mode,
            deepcopy(apprc)
        )
        self.__global_http_route: str = global_http_route
        self.__global_websocket_route: str = global_websocket_route
        self.__api_version: ApiVersion = api_version

        # Initialize bootscript
        self._bootscript_worker: BootscriptWorker = BootscriptWorker(
            bootscripts=bootscripts
        )

        self.__initialize_proxies(
            ErrorHandlers=ErrorHandlers,
            api_indication=api_indication
        )

        self.__di: Di = Di(
            root_module,
            global_modules=global_modules,
            global_middleware=global_middleware
        )

        self.__init_router()

        # Configure logging
        LogUtils.configure_log(
            validation.apply(self.__di.find("LogConfig"), LogConfig),
            app_mode_prod=AppMode.PROD
        )

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        """
        Propagates a call to the created application.
        """
        await self.app(scope, receive, send)

    @classmethod
    async def create(
        cls,
        root_module: Module,
        *,
        dotenv_path: Path | None = None,
        api_indication: Indication | None = None,
        ErrorHandlers: set[type[ErrorHandler]] | None = None,
        apprc: AppRc | None = None,
        mode: AppMode | None = None,
        global_http_route: str | None = None,
        global_websocket_route: str | None = None,
        global_modules: list[Module] | None = None,
        global_middleware: GlobalMiddlewareSetup | None = None,
        api_version: ApiVersion | None = None,
        bootscripts: list[Bootscript] | None = None
    ) -> Self:
        """
        Creates a Boot instance.

        This should be the only way to initialize a new Boot.

        Idea of using this create() method instead of traditional __init__ is
        to await important asynchronous coroutines every time a fresh boot
        is created.

        Args:
            root_module:
                Root module of the app.
            dotenv_path (optional):
                Path to .env file. Defaults to ".env".
            api_indication (optional):
                Indication object used as a convention for outcoming API
                structures. Defaults to predefined by framework's indication
                convention.
            ErrorHandlers (optional):
                List of exception handlers to add. By default framework adds
                the builtin Exception and orwynn.Error handlers.
            apprc (optional):
                Application configuration. By default environ ORWYNN_RC_PATH
                is checked if this arg is not given.
            mode (optional):
                Application mode. By default environ ORWYNN_MODE is
                checked if this arg is not given.
            global_http_route (optional):
                Global route to be prepended to every controller's route.
                Defaults to no route. Can accept formatting "{version}" for an
                API version to be injected into route.
            global_websocket_route (optional):
                Global route to be prepended to every controller's route.
                Defaults to no route. Can accept formatting "{version}" for an
                API version to be injected into route.
            global_imports (optional):
                Modules available across all other modules imported into the
                application. Note that no other instance can import a globally
                available module.
            global_middleware (optional):
                Map of middleware and its covered routes to apply globally.
                Note that every initialized Provider can be accessed from such
                middleware.
            api_version (optional):
                Object describes API versioning rules for the project. By
                default only v1 is supported.
            bootscripts (optional):
                List of bootscripts to be launched at different points of boot
                time.
        """

        boot: Boot = Boot(
            root_module,
            dotenv_path=dotenv_path,
            api_indication=api_indication,
            ErrorHandlers=ErrorHandlers,
            apprc=apprc,
            mode=mode,
            global_http_route=global_http_route,
            global_websocket_route=global_websocket_route,
            global_modules=global_modules,
            global_middleware=global_middleware,
            api_version=api_version,
            bootscripts=bootscripts,
            _fw_init_lock=False
        )

        await boot._call_bootscripts()

        return boot

    async def _call_bootscripts(self) -> None:
        """
        Calls bootscripts for all time frames.
        """
        # AFTER_ALL bootscript call time
        with contextlib.suppress(NoScriptsForCallTimeError):
            await self._bootscript_worker.call_by_time(
                CallTime.AFTER_ALL,
                self.__di._fw_container
            )

    def __initialize_mode(
        self,
        input_mode: AppMode | None
    ) -> AppMode:
        if input_mode:
            return input_mode
        else:
            return self.__parse_mode()

    def __initialize_proxies(
        self,
        ErrorHandlers: set[type[ErrorHandler]],
        api_indication: Indication
    ) -> None:
        BootProxy(
            root_dir=self.__root_dir,
            mode=self.__mode,
            api_indication=self.__api_indication,
            apprc=self.__apprc,
            ErrorHandlers=ErrorHandlers,
            global_http_route=self.__global_http_route,
            global_websocket_route=self.__global_websocket_route,
            api_version=self.__api_version
        )
        EndpointContainer()
        ApiIndicationOnlyProxy(api_indication)

    def __init_router(self) -> Router:
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
            all_exception_handlers: list[ErrorHandler] = \
                self.__di.exception_handlers
        except MissingDiObjectError:
            all_exception_handlers = []

        return Router(
            self.app,
            global_http_route=self.__global_http_route,
            global_websocket_route=self.__global_websocket_route,
            api_version=self.__api_version,
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
    def mode(self) -> AppMode:
        return self.__mode

    @property
    def api_indication(self) -> Indication:
        return self.__api_indication

    def __parse_mode(self) -> AppMode:
        mode_env: str | None = os.getenv("ORWYNN_MODE")

        if not mode_env:
            return AppMode.DEV
        else:
            return AppMode(mode_env)

    def __parse_root_dir(self) -> Path:
        root_dir: Path
        root_dir_env: str = os.getenv("ORWYNN_ROOT_DIR", "")

        root_dir = \
            Path(os.getcwd()) if not root_dir_env else Path(root_dir_env)

        if not root_dir.is_dir():
            raise NotDirError(
                f"{root_dir} is not a directory"
            )

        return root_dir

    def _check_init_lock(self, lock: bool) -> None:
        if lock:
            raise DeprecatedFeatureError(
                deprecated_feature="initializing Boot via __init__",
                use_instead="Boot.create(...)"
            )
