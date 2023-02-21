from pathlib import Path
from typing import Any, Self

from orwynn.src.apprc.AppRc import AppRc
from orwynn.src.boot.BootMode import BootMode
from orwynn.src.config.Config import Config
from orwynn.src.indication.Indication import Indication
from orwynn.src.proxy.BootProxy import BootProxy


class BootConfig(Config):
    """Contains information about boot.

    Attributes:
        mode:
            Boot mode.
        root_dir:
            Root directory of the boot.
    """
    mode: BootMode
    root_dir: Path
    api_indication: Indication
    app_rc: AppRc

    @classmethod
    def load(cls, *, extra: dict[str, Any]) -> Self:
        proxy: BootProxy = BootProxy.ie()
        return cls(
            **proxy.boot_config_data, **extra
        )
