import os
from pathlib import Path
from types import NoneType
from copy import deepcopy
from typing import Callable

import dotenv

from orwynn.app.App import App
from orwynn.app.DefaultErrorHandler import DefaultErrorHandler
from orwynn.app.DefaultExceptionHandler import DefaultExceptionHandler
from orwynn.app.DefaultHTTPExceptionHandler import DefaultHTTPExceptionHandler
from orwynn.app.DefaultRequestValidationExceptionHandler import \
    DefaultRequestValidationExceptionHandler
from orwynn.app.ErrorHandler import ErrorHandler
from orwynn.apprc.APP_RC_MODE_NESTING import APP_RC_MODE_NESTING
from orwynn.apprc.AppRC import AppRC
from orwynn.apprc.AppRCSearchError import AppRCSearchError
from orwynn.apprc.parse_apprc import parse_apprc
from orwynn.boot.BootMode import BootMode
from orwynn.boot.UnknownBootModeError import UnknownBootModeError
from orwynn.boot.UnknownSourceError import UnknownSourceError
from orwynn.cls import bind_first_arg, bind_first_arg_async
from orwynn.controller.Controller import Controller
from orwynn.controller.http.HTTPController import HTTPController
from orwynn.controller.websocket.WebsocketController import WebsocketController
from orwynn.database.UnknownDatabaseKindError import UnknownDatabaseKindError
from orwynn.di.DI import DI
from orwynn.di.missing_di_object_error import MissingDIObjectError
from orwynn.error.Error import Error
from orwynn.error.get_non_framework_exceptions import \
    get_non_framework_exceptions
from orwynn.error.MalfunctionError import MalfunctionError
from orwynn.file.NotDirError import NotDirError
from orwynn.indication.default_api_indication import default_api_indication
from orwynn.indication.Indication import Indication
from orwynn.log.configure_log import configure_log
from orwynn.log.Log import Log
from orwynn.log.LogConfig import LogConfig
from orwynn.middleware.Middleware import Middleware
from orwynn.module.Module import Module
from orwynn.mongo.Mongo import Mongo
from orwynn.mongo.MongoConfig import MongoConfig
from orwynn.mp import dictpp
from orwynn.proxy.APIIndicationOnlyProxy import APIIndicationOnlyProxy
from orwynn.proxy.BootProxy import BootProxy
from orwynn.proxy.EndpointProxy import EndpointProxy
from orwynn.router.Router import Router
from orwynn import mp, validation, web
from orwynn.file.yml import load_yml
from orwynn.service.FrameworkService import FrameworkService
from orwynn.sql.SQL import SQL
from orwynn.validation import (RequestValidationException, validate,
                                    validate_each)
from orwynn.web import CORS, HTTPException, HTTPMethod
from orwynn.worker.Worker import Worker


class Boot(Worker):
    """Worker responsible of booting an application.

    General usage is to construct this class in the main.py with required
    parameters and then access Boot.app for your needs.

    Attributes:
        root_module:
            Root module of the app.
        dotenv_path (optional)Dir:
            Path to .env file. Defaults to ".env".
        api_indication (optional):
            Indication object used as a convention for outcoming API
            structures. Defaults to predefined by framework's indication
            convention.
        cors (optional):
            CORS policy applied to the whole application. No CORS applied by
            default.
        ErrorHandlers (optional):
            List of error handlers to add. By default framework adds builtin
            Exception and orwynn.Error handlers.
        apprc (optional):
            Application configuration. By default environ Orwynn_AppRCPath is
            checked if this arg is not given.
        mode (optional):
            Application mode. By default environ Orwynn_Mode is
            checked if this arg is not given.

    Environs:
        Orwynn_Mode:
            Boot mode for application. Defaults to DEV. Alternatively you can
            pass arg "mode".
        Orwynn_RootDir:
            Root directory for application. Defaults to os.getcwd()
        Orwynn_AppRCPath:
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
    @Log.catch(reraise=True)
    def __init__(
        self,
        root_module: Module,
        *,
        dotenv_path: Path | None = None,
        api_indication: Indication | None = None,
        cors: CORS | None = None,
        ErrorHandlers: list[type[ErrorHandler]] | None = None,
        apprc: AppRC | None = None,
        mode: BootMode | None = None
    ) -> None:
        super().__init__()
        if dotenv_path is None:
            dotenv_path = Path(".env")
        validate(dotenv_path, Path)
        validate(root_module, Module)
        if api_indication is None:
            api_indication = default_api_indication
        validate(api_indication, Indication)
        validate(cors, [CORS, NoneType])
        if ErrorHandlers is None:
            ErrorHandlers = []
        validate_each(
            ErrorHandlers, ErrorHandler, expected_sequence_type=list
        )
        validate(apprc, [AppRC, NoneType])
        validate(mode, [BootMode, NoneType])

        dotenv.load_dotenv(dotenv_path, override=True)

        self.__mode: BootMode
        if mode:
            self.__mode = mode
        else:
            self.__mode = self.__parse_mode()
        self.__root_dir: Path = self.__parse_root_dir()
        self.__api_indication: Indication = api_indication
        self.__apprc: AppRC = parse_apprc(
            self.__root_dir,
            self.__mode,
            deepcopy(apprc)
        )

        # Init proxies
        BootProxy(
            root_dir=self.__root_dir,
            mode=self.__mode,
            api_indication=self.__api_indication,
            apprc=self.__apprc,
            ErrorHandlers=ErrorHandlers
        )
        EndpointProxy()
        APIIndicationOnlyProxy(api_indication)

        # Add framework services
        root_module.add_provider_or_skip(App)
        root_module.add_provider_or_skip(LogConfig)

        self.__di: DI = DI(root_module)

        self.__router: Router = Router(
            self.app
        )

        self.__configure_log()

        try:
            self.__register_routes(self.__di.modules, self.__di.controllers)
        except MissingDIObjectError:
            # Don't raise error to ease test writings
            pass
        try:
            self.__register_middleware(
                self.__di.all_middleware
            )
        except MissingDIObjectError:
            # No middleware defined, it's ok
            pass

        if cors is not None:
            self.app.configure_cors(cors)

        self.__register_error_handlers()

    @property
    def app(self) -> App:
        return self.__di.app_service

    @property
    def mode(self) -> BootMode:
        return self.__mode

    @property
    def api_indication(self) -> Indication:
        return self.__api_indication

    def __configure_log(self) -> None:
        log_config: LogConfig = validation.apply(
            self.__di.find("LogConfig"),
            LogConfig
        )
        configure_log(log_config)

    def __register_error_handlers(
        self
    ) -> None:
        error_handlers: list[ErrorHandler]
        try:
            error_handlers = self.__di.error_handlers
        except MissingDIObjectError:
            error_handlers = []

        HandledBuiltinExceptions: list[type[Exception]] = []
        is_default_error_handled: bool = False

        HandledBuiltinExceptions, is_default_error_handled = \
            self.__collect_error_handlers_data(error_handlers)

        self.__add_error_handlers(
            error_handlers=error_handlers,
            HandledBuiltinExceptions=HandledBuiltinExceptions,
            is_default_error_handled=is_default_error_handled
        )

    def __collect_error_handlers_data(
        self,
        error_handlers: list[ErrorHandler]
    ) -> tuple[list[type[Exception]], bool]:
        HandledBuiltinExceptions: list[type[Exception]] = []
        is_default_error_handled: bool = False

        for error_handler in error_handlers:
            if error_handler.E is None:
                raise MalfunctionError()
            elif isinstance(error_handler.E, list):
                for E in error_handler.E:
                    if (
                        issubclass(E, Exception)
                        and not issubclass(E, Error)
                    ):
                        HandledBuiltinExceptions.append(E)
                    elif E is Error:
                        is_default_error_handled = True
            else:
                if (
                    issubclass(error_handler.E, Exception)
                    and not issubclass(error_handler.E, Error)
                ):
                    HandledBuiltinExceptions.append(error_handler.E)
                elif error_handler.E is Error:
                    is_default_error_handled = True

        return HandledBuiltinExceptions, is_default_error_handled

    def __add_error_handlers(
        self,
        *,
        error_handlers: list[ErrorHandler],
        HandledBuiltinExceptions: list[type[Exception]],
        is_default_error_handled: bool
    ) -> None:
        # FIXME: Here default exception handlers are created without DI
        #   notifying which may raise confusion.

        # For any unhandled builtin exception add default handler,
        # also add special RequestValidationException since it's not direct
        # subclass of exception
        RemainingExceptionSubclasses = \
            get_non_framework_exceptions() + [RequestValidationException]
        for HandledException in HandledBuiltinExceptions:
            try:
                RemainingExceptionSubclasses.remove(HandledException)
            except ValueError:
                raise MalfunctionError()

        # Handle special exceptions
        if HTTPException in RemainingExceptionSubclasses:
            RemainingExceptionSubclasses.remove(HTTPException)
            self.app.add_error_handler(DefaultHTTPExceptionHandler())
        if RequestValidationException in RemainingExceptionSubclasses:
            RemainingExceptionSubclasses.remove(RequestValidationException)
            self.app.add_error_handler(
                DefaultRequestValidationExceptionHandler()
            )

        if RemainingExceptionSubclasses:
            default_exception_handler: DefaultExceptionHandler = \
                DefaultExceptionHandler()
            default_exception_handler.set_handled_exception(
                RemainingExceptionSubclasses
            )
            self.app.add_error_handler(default_exception_handler)

        if not is_default_error_handled:
            self.app.add_error_handler(DefaultErrorHandler())

        for error_handler in error_handlers:
            self.app.add_error_handler(error_handler)

    def __register_routes(
        self, modules: list[Module], controllers: list[Controller]
    ) -> None:
        for m in modules:
            for C in m.Controllers:
                self.__register_controller_class_for_module(m, C, controllers)

    def __register_middleware(self, middleware: list[Middleware]) -> None:
        for m in middleware:
            self.app.add_middleware(m)

    def __register_controller_class_for_module(
        self,
        m: Module,
        C: type[Controller],
        controllers: list[Controller]
    ) -> None:
        is_controller_found: bool = False
        for c in controllers:
            if type(c) is C:
                is_controller_found = True

                if isinstance(c, HTTPController):
                    self.__register_http_for_module(c, m)
                elif isinstance(c, WebsocketController):
                    self.__register_websocket_controller_for_module(c, m)
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
        c: HTTPController,
        m: Module
    ) -> None:
        # At least one method found
        is_method_found: bool = False
        for http_method in HTTPMethod:
            # Don't register unused methods
            if http_method in c.methods:
                is_method_found = True

                self.__router.register_route(
                    # We can concatenate routes such way since routes
                    # are validated to not contain following slash
                    # -> But join_routes() handles this situation, doesn't it?
                    route=web.join_routes(m.route, c.route),
                    fn=c.get_fn_by_http_method(http_method),
                    method=http_method
                )

        if not is_method_found:
            raise MalfunctionError(
                f"no http methods found for controller {c.__class__},"
                " this shouldn't have passed validation at Controller.__init__"
            )

    def __register_websocket_controller_for_module(
        self,
        c: WebsocketController,
        m: Module
    ) -> None:
        # Methods started from "on_" or equal to "main" should be registered.
        # "main" is assigned to MODULE_ROUTE + CONTROLLER_ROUTE directly.
        for event_handler in c.event_handlers:
            method_route: str
            if event_handler.name == "main":
                method_route = "/"
            else:
                method_route = event_handler.name


            # Final route = MODULE_ROUTE + CONTROLLER_ROUTE + METHOD_ROUTE
            self.__router.register_websocket(
                route=web.join_routes(m.route, c.route, method_route),
                # Bind actual controller instance "c" for a dynamically
                # obtained method "v"
                fn=event_handler.fn
            )

    def __parse_mode(self) -> BootMode:
        mode_env: str | None = os.getenv("Orwynn_Mode")

        if not mode_env:
            return BootMode.DEV
        else:
            return BootMode(mode_env)

    def __parse_root_dir(self) -> Path:
        root_dir: Path
        root_dir_env: str = os.getenv("Orwynn_RootDir", "")

        if not root_dir_env:
            root_dir = Path(os.getcwd())
        else:
            root_dir = Path(root_dir_env)

        if not root_dir.is_dir():
            raise NotDirError(
                f"{root_dir} is not a directory"
            )

        return root_dir
