import os
from orwynn.src.app.app_mode_enum import AppModeEnum
from orwynn.src.base.module.root_module import RootModule

from orwynn.src.base.worker.worker import Worker
from orwynn.src.app.app_service import AppService
from orwynn.src.di.di import DI


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

    # Import root module from your location, it might be `src` directory
    from .src.root_module import root_module

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
        self._mode_enum = mode_enum
        self._di: DI = DI(root_module)

    @property
    def app(self) -> AppService:
        return self._di.app