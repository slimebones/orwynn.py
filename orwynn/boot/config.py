from pathlib import Path
from typing import Any, Self

from orwynn.app import AppMode
from orwynn.apprc.apprc import AppRc
from orwynn.base.config import Config
from orwynn.indication.indication import Indication
from orwynn.proxy.boot import BootProxy


class BootConfig(Config):
    """Contains information about boot.

    Attributes:
        mode:
            Boot mode.
        root_dir:
            Root directory of the boot.
    """
    mode: AppMode
    root_dir: Path
    api_indication: Indication
    app_rc: AppRc

    @classmethod
    def load(cls, *, extra: dict[str, Any]) -> Self:
        proxy: BootProxy = BootProxy.ie()
        return cls(
            **proxy.boot_config_data, **extra
        )
