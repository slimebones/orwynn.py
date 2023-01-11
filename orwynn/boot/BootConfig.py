from pathlib import Path
from typing import Any, Self

from orwynn.apprc.AppRC import AppRC
from orwynn.boot.BootMode import BootMode
from orwynn.config.Config import Config
from orwynn.indication.Indication import Indication
from orwynn.proxy.BootProxy import BootProxy


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
    app_rc: AppRC

    @classmethod
    def load(cls, *, extra: dict[str, Any]) -> Self:
        proxy: BootProxy = BootProxy.ie()
        return cls(
            **proxy.boot_config_data, **extra
        )
