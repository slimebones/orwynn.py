from pathlib import Path
from typing import TYPE_CHECKING

from orwynn.base.worker import Worker
from orwynn.utils.scheme import Scheme

if TYPE_CHECKING:
    from orwynn.apiversion import ApiVersion
    from orwynn.app import AppMode
    from orwynn.apprc import AppRc
    from orwynn.base.errorhandler.errorhandler import ErrorHandler
    from orwynn.indication.indication import Indication


class BootProxy(Worker):
    """Proxy data to prevent DI importing Boot worker directly (and avoid
    circular imports by this) to build BootConfig.
    """
    def __init__(
        self,
        *,
        root_dir: Path,
        mode: "AppMode",
        api_indication: "Indication",
        apprc: "AppRc",
        ErrorHandlers: set[type["ErrorHandler"]],
        global_http_route: str,
        global_websocket_route: str,
        api_version: "ApiVersion"
    ) -> None:
        super().__init__()
        self.__root_dir: Path = root_dir
        self.__mode: AppMode = mode
        self.__api_indication: Indication = api_indication
        self.__apprc: AppRc = apprc
        self.__ErrorHandlers: set[type["ErrorHandler"]] = \
            ErrorHandlers
        self.__global_http_route: str = global_http_route
        self.__global_websocket_route: str = global_websocket_route
        self.__api_version: ApiVersion = api_version

    @property
    def root_dir(self) -> Path:
        return self.__root_dir

    @property
    def mode(self) -> "AppMode":
        return self.__mode

    @property
    def api_indication(self) -> "Indication":
        return self.__api_indication

    @property
    def apprc(self) -> "AppRc":
        return self.__apprc

    @property
    def ErrorHandlers(self) -> set[type["ErrorHandler"]]:
        return self.__ErrorHandlers

    @property
    def global_http_route(self) -> str:
        return self.__global_http_route

    @property
    def global_websocket_route(self) -> str:
        return self.__global_websocket_route

    @property
    def api_version(self) -> "ApiVersion":
        return self.__api_version

    @property
    def boot_config_data(self) -> dict:
        return {
            "root_dir": self.__root_dir,
            "mode": self.__mode,
            "api_indication": self.__api_indication,
            "app_rc": self.__apprc,
            "ErrorHandlers": self.__ErrorHandlers
        }

    @property
    def data(self) -> dict:
        return dict(**self.boot_config_data, **{})

    def get_global_route_for_protocol(
        self,
        protocol: Scheme
    ) -> str:
        if protocol is Scheme.HTTP:
            return self.__global_http_route
        elif protocol is Scheme.WEBSOCKET:
            return self.__global_websocket_route
        else:
            raise TypeError(
                f"unrecognized protocol {protocol}"
            )
