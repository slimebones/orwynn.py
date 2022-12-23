from pathlib import Path
from typing import Any, Self
from orwynn.base.config.Config import Config
from orwynn.base.indication._Indication import Indication
from orwynn.app_rc.AppRC import AppRC
from orwynn.proxy.BootProxy import BootProxy
from orwynn.boot._BootMode import BootMode


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
