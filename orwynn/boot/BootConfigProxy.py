from orwynn.base.model.model import Model
from orwynn.base.worker.worker import Worker
from orwynn.boot.boot_mode import BootMode


class BootConfigProxy(Worker):
    """Proxy data to prevent DI importing Boot worker directly (and avoid
    circular imports by this) to build BootConfig.
    """
    def __init__(
        self,
        *,
        root_dir: str,
        mode: BootMode,
        APISchema: type[Model]
    ) -> None:
        super().__init__()
        self.__root_dir: str = root_dir
        self.__mode: BootMode = mode
        self.__APISchema: type[Model] = APISchema

    @property
    def data(self) -> dict:
        return {
            "root_dir": self.__root_dir,
            "mode": self.__mode,
            "APISchema": self.__APISchema
        }
