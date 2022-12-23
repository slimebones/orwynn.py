import os
from pathlib import Path
import re
from types import NoneType
from typing import TYPE_CHECKING

import dotenv

from orwynn.app_rc.APP_RC_MODE_NESTING import APP_RC_MODE_NESTING
from orwynn.proxy.APIIndicationOnlyProxy import APIIndicationOnlyProxy
from orwynn.proxy.SpecsProxy import SpecsProxy
from orwynn.base.database.DatabaseKind import DatabaseKind
from orwynn.base.database.UnknownDatabaseKindError import \
    UnknownDatabaseKindError
from orwynn.app.DefaultExceptionHandler import DefaultExceptionHandler
from orwynn.app.DefaultErrorHandler import DefaultErrorHandler
from orwynn.base.error.Error import Error
from orwynn.base.error.MalfunctionError import MalfunctionError
from orwynn.base.indication.default_api_indication import \
    default_api_indication
from orwynn.base.indication.Indication import Indication
from orwynn.base.middleware.Middleware import Middleware
from orwynn.base.module.Module import Module
from orwynn.base.worker._Worker import Worker
from orwynn.app_rc.AppRC import AppRC
from orwynn.app_rc.AppRCSearchError import AppRCSearchError
from orwynn.proxy.BootProxy import BootProxy
from orwynn.boot._BootMode import BootMode
from orwynn.boot.UnknownSourceError import UnknownSourceError
from orwynn.boot.UnknownBootModeError import UnknownBootModeError
from orwynn.di.DI import DI
from orwynn.di.missing_di_object_error import MissingDIObjectError
from orwynn.mongo.Mongo import Mongo
from orwynn.mongo.MongoConfig import MongoConfig
from orwynn.router.Router import Router
from orwynn.util import web
from orwynn.util.file.NotDirError import NotDirError
from orwynn.util.file.yml import load_yml
from orwynn.util.web import CORS, HTTPMethod
from orwynn.util.validation import validate, validate_each
from orwynn.app.AppService import AppService
from orwynn.app.ErrorHandler import ErrorHandler
from orwynn.base.controller.Controller import Controller


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
        databases (optional):
            List of database kinds enabled. No databases enabled by default.
        cors (optional):
            CORS policy applied to the whole application. No CORS applied by
            default.
        ErrorHandlers (optional)
            List of error handlers to add. By default framework adds builtin
            Exception and orwynn.Error handlers.

    Environs:
        Orwynn_Mode:
            Boot mode for application. Defaults to DEV.
        Orwynn_RootDir:
            Root directory for application. Defaults to os.getcwd()
        Orwynn_AppRCDir:
            Directory where application configs is located. Defaults to root
            directory.

    Usage:
    ```py
    # main.py
    from orwynn import Boot, AppModeEnum, AppService, MongoService

    # Import root module from your location
    from .myproject.root_module import root_module

    app = Boot(
        mode=AppModeEnum.DEV,
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
        databases: list[DatabaseKind] | None = None,
        cors: CORS | None = None,
        ErrorHandlers: list[type[ErrorHandler]] | None = None
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

        dotenv.load_dotenv(dotenv_path, override=True)

        self.__mode: BootMode = self.__parse_mode()
        self.__root_dir: Path = self.__parse_root_dir()
        self.__api_indication: Indication = api_indication
        self.__app_rc: AppRC = self.__parse_app_rc(
            self.__root_dir,
            self.__mode
        )

        # Init proxies
        BootProxy(
            root_dir=self.__root_dir,
            mode=self.__mode,
            api_indication=self.__api_indication,
            app_rc=self.__app_rc,
            ErrorHandlers=ErrorHandlers
        )
        SpecsProxy()
        APIIndicationOnlyProxy(api_indication)

        if databases is None:
            databases = []
        else:
            validate_each(databases, DatabaseKind, expected_sequence_type=list)

        # Add crucial builtin objects
        root_module.add_provider_or_skip(AppService)

        self.__enable_databases(databases)
        self.__di: DI = DI(root_module)

        self.__router: Router = Router(
            self.app
        )

        try:
            self.__register_routes(self.__di.modules, self.__di.controllers)
        except MissingDIObjectError:
            raise ValueError(
                "no controllers defined for this application"
            )
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
    def app(self) -> AppService:
        return self.__di.app_service

    @property
    def mode(self) -> BootMode:
        return self.__mode

    @property
    def api_indication(self) -> Indication:
        return self.__api_indication

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

        # Checking loop
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

        # For any unhandled builtin exception add default handler
        RemainingExceptionSubclasses = Exception.__subclasses__()
        for HandledException in HandledBuiltinExceptions:
            try:
                RemainingExceptionSubclasses.remove(HandledException)
            except ValueError:
                raise MalfunctionError()

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
                self.__register_controller_for_module(c, m)
        if not is_controller_found:
            raise MalfunctionError(
                f"no initialized controller found for class {C},"
                f" but it was declared in imported module {m},"
                " so DI should have been initialized it"
            )

    def __register_controller_for_module(
        self,
        c: Controller,
        m: Module
    ) -> None:
        # At least one method found
        is_method_found: bool = False
        for http_method in HTTPMethod:
            # Don't register unused methods
            if http_method in c.methods:
                is_method_found = True

                self.__router.register_route_fn(
                    # We can concatenate routes such way since routes
                    # are validated to not contain following slash
                    route=web.join_routes(m.route, c.route),
                    fn=c.get_fn_by_http_method(http_method),
                    method=http_method
                )

        if not is_method_found:
            raise MalfunctionError(
                f"no http methods found for controller {c.__class__},"
                " this shouldn't have passed validation at Controller.__init__"
            )

    def __parse_mode(self) -> BootMode:
        mode_env: str | None = os.getenv("Orwynn_Mode")

        if not mode_env:
            return BootMode.DEV
        else:
            return self._parse_mode_from_str(mode_env)

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

    def __parse_app_rc(self, root_dir: Path, mode: BootMode) -> AppRC:
        rc_env: str = os.getenv(
            "Orwynn_AppRCDir",
            ""
        )
        should_raise_search_error: bool

        rc_dir: Path
        if not rc_env:
            rc_dir = root_dir
            # On default assignment no errors raised if files not found / empty
            should_raise_search_error = False
        else:
            rc_dir = Path(rc_env)
            should_raise_search_error = True

        if Path(rc_env).exists():
            if not rc_dir.is_dir():
                raise NotDirError(
                    f"{rc_dir} is not a directory"
                )
            app_rc: AppRC = {}
            mode_nesting_index: int = APP_RC_MODE_NESTING.index(mode)
            # Load from bottom to top updating previous one with newest one
            for nesting_mode in APP_RC_MODE_NESTING[:mode_nesting_index + 1]:
                try:
                    app_rc.update(
                        self.__load_appropriate_app_rc(
                            rc_dir,
                            nesting_mode
                        )
                    )
                except AppRCSearchError:
                    continue
            if app_rc == {} and should_raise_search_error:
                raise AppRCSearchError(
                    f"loading rc files from dir {rc_dir} hasn't had any effect"
                    " - no files present (at least prod config) or they are"
                    " empty"
                )
            return app_rc
        elif (
            rc_env.startswith("http://")
            or rc_env.startswith("https://")
        ):
            raise NotImplementedError("URL sources are not yet implemented")
        else:
            raise UnknownSourceError(
                f"unknown source {rc_env}"
            )

    def __load_appropriate_app_rc(self, rc_dir: Path, mode: BootMode) -> AppRC:
        for f in rc_dir.iterdir():
            try:
                prelast_suffix, last_suffix = f.suffixes[len(f.suffixes) - 2:]
            except ValueError:
                # Not enough values to unpack
                continue

            if (
                re.match(r"^apprc\..+\..+$", f.name.lower())
                and prelast_suffix.lower() == "." + mode.value.lower()
                and last_suffix.lower() in [".yml", ".yaml"]
            ):
                return load_yml(f)

        raise AppRCSearchError(
            f"cannot find apprc for mode {mode} in directory {rc_dir}"
        )

    @staticmethod
    def _parse_mode_from_str(mode: str) -> BootMode:
        match mode:
            case "test":
                return BootMode.TEST
            case  "dev":
                return BootMode.DEV
            case  "prod":
                return BootMode.PROD
            case _:
                raise UnknownBootModeError(f"unknown mode {mode}")

    def __enable_databases(self, database_kinds: list[DatabaseKind]) -> None:
        for kind in database_kinds:
            match kind:
                case DatabaseKind.MONGO:
                    Mongo(
                        config=MongoConfig.load()
                    )
                case DatabaseKind.POSTRGRESQL:
                    raise NotImplementedError(
                        "postgresql database currently not supported"
                    )
                case _:
                    raise UnknownDatabaseKindError(
                        f"unknown database kind {kind}"
                    )
