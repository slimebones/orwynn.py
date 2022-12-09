import os
from orwynn.app.app_mode_enum import AppModeEnum
from orwynn.base.module.root_module import RootModule

from orwynn.base.worker.worker import Worker
from orwynn.app.app_service import AppService
from orwynn.di.di import DI
from orwynn.util.validation import validate


class Boot(Worker):
    """Worker responsible of booting an application.
    
    General usage is to construct this class in the main.py with required
    parameters and then access Boot.app for your needs.

    Attributes:
        mode_enum:
            Selected mode for the app.
        root_module:
            Root module of the app. 
        root_dir (optional):
            Root directory of the project. Defaults to os.getcwd().

    Usage:
    ```py
    # main.py
    from orwynn import Boot, AppModeEnum

    # Import root module from your location
    from .myproject.root_module import root_module

    app = Boot(
        mode_enum=AppModeEnum.DEV,
        root_module=root_module
    ).app
    ```
    """
    def __init__(
        self,
        mode_enum: AppModeEnum,
        root_module: RootModule
    ) -> None:
        super().__init__()

        validate(mode_enum, AppModeEnum)
        validate(root_module, RootModule)

        self._mode_enum = mode_enum
        self._di: DI = DI(root_module)

    @property
    def app(self) -> AppService:
        return self._di.find("app_service")