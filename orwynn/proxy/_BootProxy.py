from pathlib import Path
from typing import TYPE_CHECKING

from orwynn.apprc._AppRc import AppRc
from orwynn.boot.api_version.ApiVersion import ApiVersion
from orwynn.boot._BootMode import BootMode
from orwynn.util.Protocol import Protocol
from orwynn.worker._Worker import Worker

if TYPE_CHECKING:
    from orwynn.base.exchandler._ExceptionHandler import ExceptionHandler
    from orwynn.indication._Indication import Indication


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
        global_http_route: str,
        global_websocket_route: str,
        api_version: ApiVersion
    ) -> None:
        super().__init__()
        self.__root_dir: Path = root_dir
        self.__mode: BootMode = mode
        self.__api_indication: Indication = api_indication
        self.__apprc: AppRc = apprc
        self.__ExceptionHandlers: set[type["ExceptionHandler"]] = \
            ExceptionHandlers
        self.__global_http_route: str = global_http_route
        self.__global_websocket_route: str = global_websocket_route
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
    def global_http_route(self) -> str:
        return self.__global_http_route

    @property
    def global_websocket_route(self) -> str:
        return self.__global_websocket_route

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

    def get_global_route_for_protocol(
        self,
        protocol: Protocol
    ) -> str:
        if protocol is Protocol.HTTP:
            return self.__global_http_route
        elif protocol is Protocol.WEBSOCKET:
            return self.__global_websocket_route
        else:
            raise TypeError(
                f"unrecognized protocol {protocol}"
            )
