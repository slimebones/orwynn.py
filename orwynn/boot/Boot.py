import contextlib
import os
from copy import deepcopy
from pathlib import Path
from types import NoneType
from typing import Literal, Optional, Sequence

import dotenv

from orwynn import validation, web
from orwynn.app.App import App
from orwynn.apprc.AppRc import AppRc
from orwynn.apprc.parse_apprc import parse_apprc
from orwynn.boot.api_version.ApiVersion import ApiVersion
from orwynn.boot.BootMode import BootMode
from orwynn.BUILTIN_MIDDLEWARE import (
    BUILTIN_HTTP_MIDDLEWARE,
    BUILTIN_WEBSOCKET_MIDDLEWARE,
)
from orwynn.controller.Controller import Controller
from orwynn.controller.http.HttpController import HttpController
from orwynn.controller.websocket.WebsocketController import WebsocketController
from orwynn.di.Di import Di
from orwynn.di.MissingDiObjectError import MissingDiObjectError
from orwynn.error.catching.ExceptionHandler import ExceptionHandler
from orwynn.error.catching.ExceptionHandlerManager import ExceptionHandlerManager
from orwynn.error.MalfunctionError import MalfunctionError
from orwynn.file.NotDirError import NotDirError
from orwynn.indication.default_api_indication import default_api_indication
from orwynn.indication.Indication import Indication
from orwynn.log.configure_log import configure_log
from orwynn.log.LogConfig import LogConfig
from orwynn.middleware.BuiltinHttpMiddleware import BuiltinHttpMiddleware
from orwynn.middleware.BuiltinWebsocketMiddleware import (
    BuiltinWebsocketMiddleware,
)
from orwynn.middleware.Middleware import Middleware
from orwynn.middleware.MiddlewareRegister import MiddlewareRegister
from orwynn.module.Module import Module
from orwynn.proxy.APIIndicationOnlyProxy import APIIndicationOnlyProxy
from orwynn.proxy.BootProxy import BootProxy
from orwynn.proxy.EndpointProxy import EndpointProxy
from orwynn.router.Router import Router
from orwynn.validation import (
    validate,
    validate_each,
)
from orwynn.web import Cors, HttpMethod
from orwynn.web.Protocol import Protocol
from orwynn.worker.Worker import Worker


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
        global_route (optional):
            Global route to be prepended to every controller's route. Defaults
            to no route. Can accept formatting "{version}" for an API version
            to be injected into route.
        global_imports (optional):
            Modules available across all other modules imported into the
            application. Note that no other instance can import a globally
            available module.
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
        global_route: str | None = None,
        global_modules: list[Module] | None = None,
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

        if global_route is None:
            global_route = ""
        validate(global_route, str)

        if global_modules is None:
            global_modules = []
        validate_each(global_modules, Module, expected_sequence_type=list)

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
        self.__global_route: str = global_route
        self.__api_version: ApiVersion = api_version

        # Init proxies
        BootProxy(
            root_dir=self.__root_dir,
            mode=self.__mode,
            api_indication=self.__api_indication,
            apprc=self.__apprc,
            ExceptionHandlers=ExceptionHandlers,
            global_route=self.__global_route,
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

        self.__di: Di = Di(root_module, global_modules=global_modules)

        # Configure logging
        configure_log(validation.apply(self.__di.find("LogConfig"), LogConfig))

        self.__router: Router = Router(
            self.app
        )

        # Add middleware, it should be done before the controller's
        # adding due to the special websocket middleware registering
        self.__add_middleware(cors)

        # Supress: Don't raise error to ease test writings
        with contextlib.suppress(MissingDiObjectError):
            self.__register_routes(self.__di.modules, self.__di.controllers)

        # Register websockets after adding middleware and controllers
        self.__router.register_websocket_layers()

    @property
    def app(self) -> App:
        return self.__di.app_service

    @property
    def mode(self) -> BootMode:
        return self.__mode

    @property
    def api_indication(self) -> Indication:
        return self.__api_indication

    def __register_routes(
        self, modules: list[Module], controllers: list[Controller]
    ) -> None:
        for m in modules:
            for C in m.Controllers:
                self.__register_controller_class_for_module(m, C, controllers)

    def __register_controller_class_for_module(
        self,
        m: Module,
        C: type[Controller],
        controllers: list[Controller]
    ) -> None:
        if m.route is None:
            raise MalfunctionError(
                f"module {m} has not route and shouldn't have added any"
                " controllers"
            )

        is_controller_found: bool = False
        for c in controllers:
            if type(c) is C:
                is_controller_found = True

                if isinstance(c, HttpController):
                    self.__register_http_for_module(c, m)
                elif isinstance(c, WebsocketController):
                    self.__router.add_websocket_controller(
                        c,
                        module_route=m.route
                    )
                else:
                    raise TypeError(
                        f"controller unsupported type {type(c)}"
                    )
        if not is_controller_found:
            raise MalfunctionError(
                f"no initialized controller found for class {C},"
                f" but it was declared in imported module {m},"
                " so DI should have been initialized it"
            )

    def __register_http_for_module(
        self,
        controller: HttpController,
        module: Module
    ) -> None:
        # At least one method found
        is_method_found: bool = False
        for http_method in HttpMethod:
            # Don't register unused methods
            if http_method in controller.methods:
                is_method_found = True

                routes: set[str] = self.__get_routes_for_http_controller(
                    controller,
                    module
                )

                for route in routes:
                    self.__router.register_route(
                        route=route,
                        fn=controller.get_fn_by_http_method(http_method),
                        method=http_method
                    )

        if not is_method_found:
            raise MalfunctionError(
                f"no http methods found for controller {controller.__class__},"
                " this shouldn't have passed validation at Controller.__init__"
            )

    def __get_routes_for_http_controller(
        self,
        controller: HttpController,
        module: Module
    ) -> set[str]:
        """Returns all http routes which given controller accessible from.
        """
        if module.route is None:
            raise MalfunctionError(
                f"module {module} has not route and shouldn't have added any"
                " controllers"
            )

        routes: set[str] = set()
        final_versions: set[int] = set()
        version: int | set[int] | None | Literal["*"] = controller.VERSION

        # Get the latest version if none is specified for controller
        if version is None:
            final_versions.add(self.__api_version.latest)
        elif isinstance(version, int):
            final_versions.add(version)
        elif isinstance(version, set):
            final_versions.update(version)
        elif isinstance(version, str):
            if version != "*":
                raise MalfunctionError(
                    f"version cannot be {version}, a validatation check should"
                    " have been performed at HTTPController"
                )
            # Add all supported versions
            final_versions.update(self.__api_version.supported)
        else:
            raise MalfunctionError(
                f"unrecognized version {version}, a validation check should"
                " have been performed at HTTPController"
            )

        for v in final_versions:
            self.__api_version.check_if_supported(v)

            # We can concatenate routes such way since routes
            # are validated to not contain following slash
            # -> But join_routes() handles this situation, doesn't it?
            concatenated_route: str = web.join_routes(
                self.__global_route.replace(
                    "{version}",
                    str(v)
                ),
                module.route,
                controller.route
            )
            routes.add(concatenated_route)

        return routes

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

    def __add_middleware(self, cors: Optional[Cors]) -> None:
        user_exception_handlers: set[ExceptionHandler]
        try:
            user_exception_handlers = set(self.__di.exception_handlers)
        except MissingDiObjectError:
            user_exception_handlers = set()

        user_middleware: list[Middleware]
        try:
            user_middleware = self.__di.all_middleware
        except MissingDiObjectError:
            user_middleware = []

        MiddlewareRegister(
            middleware_register=self.__router.add_middleware
        ).register(
            user_middleware=user_middleware,
            user_exception_handlers=user_exception_handlers,
            cors=cors
        )
