from typing import TYPE_CHECKING
from orwynn.base.worker.worker import Worker
from orwynn.boot.boot_mode import BootMode

if TYPE_CHECKING:
    from orwynn.base.indication.indication import Indication


class BootDataProxy(Worker):
    """Proxy data to prevent DI importing Boot worker directly (and avoid
    circular imports by this) to build BootConfig.
    """
    def __init__(
        self,
        *,
        root_dir: str,
        mode: BootMode,
        api_indication: "Indication"
    ) -> None:
        super().__init__()
        self.__root_dir: str = root_dir
        self.__mode: BootMode = mode
        self.__api_indication: Indication = api_indication

    @property
    def api_indication(self) -> "Indication":
        return self.__api_indication

    @property
    def data(self) -> dict:
        return {
            "root_dir": self.__root_dir,
            "mode": self.__mode,
            "api_indication": self.__api_indication
        }
