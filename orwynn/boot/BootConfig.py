from pathlib import Path
from typing import Any, Self
from orwynn.base.config.Config import Config
from orwynn.base.indication._Indication import Indication
from orwynn.app_rc.AppRC import AppRC
from orwynn.boot._BootDataProxy import BootDataProxy
from orwynn.boot.BootMode import BootMode


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
        proxy: BootDataProxy = BootDataProxy.ie()
        return cls(
            **proxy.boot_config_data, **extra
        )
