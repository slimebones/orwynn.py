from typing import Any, Self
from orwynn.base.config.Config import Config
from orwynn.base.indication.Indication import Indication
from orwynn.boot.AppRC import AppRC
from orwynn.boot.BootDataProxy import BootDataProxy
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
    root_dir: str
    api_indication: Indication
    apprc: AppRC

    @classmethod
    def load(cls, *, extra: dict[str, Any]) -> Self:
        proxy: BootDataProxy = BootDataProxy.ie()
        return cls(
            **proxy.boot_config_data, **extra
        )
