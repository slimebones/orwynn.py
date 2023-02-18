from pathlib import Path
from typing import TYPE_CHECKING

from orwynn.apprc.AppRc import AppRc
from orwynn.boot.api_version.ApiVersion import ApiVersion
from orwynn.boot.BootMode import BootMode
from orwynn.worker.Worker import Worker

if TYPE_CHECKING:
    from orwynn.error.catching.ExceptionHandler import ExceptionHandler
    from orwynn.indication.Indication import Indication


class BootProxy(Worker):
    """Proxy data to prevent DI importing Boot worker directly (and avoid
    circular imports by this) to build BootConfig.
    """
    def __init__(
        self,
        *,
        root_dir: Path,
        mode: BootMode,
        api_indication: "Indication",
        apprc: AppRc,
        ExceptionHandlers: set[type["ExceptionHandler"]],
        global_route: str,
        api_version: ApiVersion
    ) -> None:
        super().__init__()
        self.__root_dir: Path = root_dir
        self.__mode: BootMode = mode
        self.__api_indication: Indication = api_indication
        self.__apprc: AppRc = apprc
        self.__ExceptionHandlers: set[type["ExceptionHandler"]] = \
            ExceptionHandlers
        self.__global_route: str = global_route
        self.__api_version: ApiVersion = api_version

    @property
    def mode(self) -> BootMode:
        return self.__mode

    @property
    def api_indication(self) -> "Indication":
        return self.__api_indication

    @property
    def apprc(self) -> AppRc:
        return self.__apprc

    @property
    def ExceptionHandlers(self) -> set[type["ExceptionHandler"]]:
        return self.__ExceptionHandlers

    @property
    def global_route(self) -> str:
        return self.__global_route

    @property
    def api_version(self) -> ApiVersion:
        return self.__api_version

    @property
    def boot_config_data(self) -> dict:
        return {
            "root_dir": self.__root_dir,
            "mode": self.__mode,
            "api_indication": self.__api_indication,
            "app_rc": self.__apprc,
            "ErrorHandlers": self.__ExceptionHandlers
        }

    @property
    def data(self) -> dict:
        return dict(**self.boot_config_data, **{})
