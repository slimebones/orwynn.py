import os
from types import NoneType

from orwynn.app.AppService import AppService
from orwynn.base.config import fw_create_config
from orwynn.base.controller.Controller import Controller
from orwynn.base.database.DatabaseKind import DatabaseKind
from orwynn.base.database.UnknownDatabaseKindError import \
    UnknownDatabaseKindError
from orwynn.base.error.malfunction_error import MalfunctionError
from orwynn.base.indication.default_api_indication import \
    default_api_indication
from orwynn.base.indication.Indication import Indication
from orwynn.base.module.Module import Module
from orwynn.base.worker.Worker import Worker
from orwynn.boot.BootDataProxy import BootDataProxy
from orwynn.boot.BootMode import BootMode
from orwynn.boot.UnsupportedBootModeError import UnsupportedBootModeError
from orwynn.di.DI import DI
from orwynn.mongo.Mongo import Mongo
from orwynn.mongo.MongoConfig import MongoConfig
from orwynn.util.http.http import HTTPMethod
from orwynn.util.validation import validate


class Boot(Worker):
    """Worker responsible of booting an application.

    General usage is to construct this class in the main.py with required
    parameters and then access Boot.app for your needs.

    Attributes:
        root_module:
            Root module of the app.
        api_indication (optional):
            Indication object used as a convention for outcoming API
            structures. Defaults to predefined by framework's indication
            convention.
        databases (optional):
            List of database kinds enabled.

    Environs:
        Orwynn_Mode:
            Boot mode for application.
        Orwynn_RootDir:
            Root directory for application.
        Orwynn_UnitedSource:
            Source for configs with united source types.

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
        mode: BootMode | str | None = None,
        root_dir: str = os.getcwd(),
        api_indication: Indication | None = None,
        databases: list[DatabaseKind] | None = None
    ) -> None:
        super().__init__()
        validate(mode, [BootMode, str, NoneType])
        validate(root_module, Module)
        validate(root_dir, str)
        if not api_indication:
            api_indication = default_api_indication
        validate(api_indication, Indication)

        self.__mode: BootMode = self._parse_mode(mode)
        self.__root_dir: str = root_dir
        self.__api_indication: Indication = api_indication
        BootDataProxy(
            root_dir=self.__root_dir,
            mode=self.__mode,
            api_indication=self.__api_indication
        )

        if databases is None:
            databases = []
        else:
            validate(databases, list)

        # FIXME:
        #   Add AppService to be always initialized - THIS IS VERY BAD approach
        #   and is breaking many principles, so fix it ASAP.
        #
        #   Case is, that if no acceptor/module in the app requires AppService,
        #   it won't be included at all.
        root_module._Providers.append(AppService)

        self._di: DI = DI(root_module)

        self._register_routes(self._di.modules, self._di.controllers)

    @property
    def app(self) -> AppService:
        return self._di.app_service

    @property
    def api_indication(self) -> Indication:
        return self.__api_indication

    def _register_routes(
        self, modules: list[Module], controllers: list[Controller]
    ) -> None:
        for m in modules:
            for C in m.Controllers:
                self._register_controller_class_for_module(m, C, controllers)

    def _register_controller_class_for_module(
        self,
        m: Module,
        C: type[Controller],
        controllers: list[Controller]
    ) -> None:
        is_controller_found: bool = False
        for c in controllers:
            if type(c) is C:
                is_controller_found = True
                self._register_controller_for_module(c, m)
        if not is_controller_found:
            raise MalfunctionError(
                f"no initialized controller found for class {C},"
                f" but it was declared in imported module {m},"
                " so DI should have been initialized it"
            )

    def _register_controller_for_module(
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
                if c.ROUTE is None:
                    raise MalfunctionError(
                        f"route of controller {c.__class__} is None"
                        " but check should have been performed at"
                        " class instance initialization"
                    )

                joined_route: str
                if m.ROUTE == "/":
                    joined_route = c.ROUTE
                else:
                    joined_route = m.ROUTE + c.ROUTE

                self.app.register_route_fn(
                    # We can concatenate routes such way since routes
                    # are validated to not contain following slash
                    route=joined_route,
                    fn=c.get_fn_by_http_method(http_method),
                    method=http_method
                )

        if not is_method_found:
            raise MalfunctionError(
                f"no http methods found for controller {c.__class__},"
                " this shouldn't have passed validation at Controller.__init__"
            )

    def _parse_mode(self, mode: BootMode | str | None) -> BootMode:
        if mode is None:
            env_mode: str | None = os.getenv("Orwynn_Mode")
            if not env_mode:
                return BootMode.DEV
            else:
                return self._parse_mode_from_str(env_mode)
        elif type(mode) is str:
            return self._parse_mode_from_str(mode)
        elif type(mode) is BootMode:
            return mode
        else:
            raise

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
                raise UnsupportedBootModeError("unsupported mode {mode}")

    def __enable_databases(self, database_kinds: list[DatabaseKind]) -> None:
        for kind in database_kinds:
            match kind:
                case DatabaseKind.MONGO:
                    Mongo(
                        config=fw_create_config(MongoConfig)
                    )
                case DatabaseKind.POSTRGRESQL:
                    raise NotImplementedError(
                        "postgresql database currently not supported"
                    )
                case _:
                    raise UnknownDatabaseKindError(
                        f"unknown database kind {kind}"
                    )
