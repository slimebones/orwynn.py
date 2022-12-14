import os
from orwynn.boot.BOOT_CONFIG_PROXY_DATA import BOOT_CONFIG_PROXY_DATA
from orwynn.boot.boot_mode import BootMode
from orwynn.base.controller.controller import Controller
from orwynn.base.module.module import Module

from orwynn.base.worker.worker import Worker
from orwynn.app.app_service import AppService
from orwynn.boot.boot_error import BootError
from orwynn.di.di import DI
from orwynn.validation import validate


class Boot(Worker):
    """Worker responsible of booting an application.

    General usage is to construct this class in the main.py with required
    parameters and then access Boot.app for your needs.

    Attributes:
        mode:
            Selected mode for the app. It can be AppModeEnum or string for
            simplicity.
        root_module:
            Root module of the app.
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
        *,
        mode: BootMode | str,
        root_module: Module,
        root_dir: str = os.getcwd()
    ) -> None:
        super().__init__()
        validate(mode, [BootMode, str])
        validate(root_module, Module)
        validate(root_dir, str)

        self._mode: BootMode = self._parse_mode_enum(mode)
        self._root_dir = root_dir
        BOOT_CONFIG_PROXY_DATA.mode = self._mode
        BOOT_CONFIG_PROXY_DATA.root_dir = self._root_dir

        self._di: DI = DI(root_module)

    @property
    def app(self) -> AppService:
        return self._di.app_service

    def _register_controllers(self, controllers: list[Controller]) -> None:
        for c in controllers:
            self.app

    def _parse_mode_enum(self, mode: BootMode | str) -> BootMode:
        if type(mode) is str:
            return self._parse_mode_enum_from_str(mode)
        elif type(mode) is BootMode:
            return mode
        else:
            raise

    @staticmethod
    def _parse_mode_enum_from_str(mode: str) -> BootMode:
        match mode:
            case "test":
                return BootMode.TEST
            case  "dev":
                return BootMode.DEV
            case  "prod":
                return BootMode.PROD
            case _:
                raise BootError("Unrecognized mode: {}".format(mode))
