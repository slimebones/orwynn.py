import os
from types import NoneType
from orwynn.base.error.malfunction_error import MalfunctionError
from orwynn.boot.BOOT_CONFIG_PROXY_DATA import BOOT_CONFIG_PROXY_DATA
from orwynn.boot.boot_mode import BootMode
from orwynn.base.controller.controller import Controller
from orwynn.base.module.module import Module

from orwynn.base.worker.worker import Worker
from orwynn.app.app_service import AppService
from orwynn.boot.unsupported_boot_mode_error import UnsupportedBootModeError
from orwynn.di.di import DI
from orwynn.http import HTTPMethod
from orwynn.validation import validate


class Boot(Worker):
    """Worker responsible of booting an application.

    General usage is to construct this class in the main.py with required
    parameters and then access Boot.app for your needs.

    Attributes:
        root_module:
            Root module of the app.
        mode (optional):
            Selected mode for the app. It can be BootMode or just string for
            simplicity. Defaults to environment variable ORWYNN_MODE or to
            "dev" if such environ is not found.
        root_dir (optional):
            Root directory of the project. Defaults to os.getcwd().

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
        root_dir: str = os.getcwd()
    ) -> None:
        super().__init__()
        validate(mode, [BootMode, str, NoneType])
        validate(root_module, Module)
        validate(root_dir, str)

        self._mode: BootMode = self._parse_mode(mode)
        self._root_dir = root_dir
        BOOT_CONFIG_PROXY_DATA.mode = self._mode
        BOOT_CONFIG_PROXY_DATA.root_dir = self._root_dir

        # TEMP:
        #   Add AppService to be always initialized - THIS IS VERY BAD approach
        #   and is breaking many principles, so fix it ASAP
        root_module._Providers.append(AppService)

        self._di: DI = DI(root_module)

        self._register_routes(self._di.modules, self._di.controllers)

    @property
    def app(self) -> AppService:
        return self._di.app_service

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
        for controller_declared_method in c.METHODS
        for method in HTTPMethod:
            try:
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
                    fn=c.get_fn_by_http_method(method),
                    method=method
                )
            # To not register not implemented methods and to not
            # confuse OPTIONS requests
            except NotImplementedError:
                continue

    def _parse_mode(self, mode: BootMode | str | None) -> BootMode:
        if mode is None:
            env_mode: str | None = os.getenv("ORWYNN_MODE")
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
