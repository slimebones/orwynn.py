import os
from orwynn.app.app_mode_enum import AppModeEnum
from orwynn.base.module.module import Module
from orwynn.base.service.framework_service import FrameworkService

from orwynn.base.worker.worker import Worker
from orwynn.app.app_service import AppService
from orwynn.boot.boot_error import BootError
from orwynn.di.di import DI
from orwynn.util.validation import validate, validate_each


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
        FrameworkServices (optional):
            List of framework services to enable. AppService always included,
            even if you pass an empty list.
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
        root_module=root_module,
        FrameworkServices=[AppService, MongoService]
    ).app
    ```
    """
    def __init__(
        self,
        *,
        mode: AppModeEnum | str,
        root_module: Module,
        FrameworkServices: list[type[FrameworkService]] | None = None,
        root_dir: str = os.getcwd()
    ) -> None:
        super().__init__()

        validate(mode, [AppModeEnum, str])
        validate(root_module, Module)
        if FrameworkServices:
            validate_each(FrameworkServices, FrameworkService)
            if AppService not in FrameworkServices:
                # Preserve correct order
                FrameworkServices = [AppService] + FrameworkServices
        else:
            FrameworkServices = [AppService]
        validate(root_dir, str)

        self._mode_enum: AppModeEnum = self._parse_mode_enum(mode)
        self._root_dir = root_dir

        self._di: DI = DI(root_module)

    @property
    def app(self) -> AppService:
        return self._di.app_service

    def _parse_mode_enum(self, mode: AppModeEnum | str) -> AppModeEnum:
        if type(mode) is str:
            return self._parse_mode_enum_from_str(mode)
        elif type(mode) is AppModeEnum:
            return mode
        else:
            raise

    @staticmethod
    def _parse_mode_enum_from_str(mode: str) -> AppModeEnum:
        match mode:
            case "test":
                return AppModeEnum.TEST
            case  "dev":
                return AppModeEnum.DEV
            case  "prod":
                return AppModeEnum.PROD
            case _:
                raise BootError("Unrecognized mode: {}".format(mode))
