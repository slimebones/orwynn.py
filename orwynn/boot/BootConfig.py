from orwynn.base.config.Config import Config
from orwynn.base.config.config_source.ConfigSource import ConfigSource
from orwynn.base.config.config_source.ConfigSourceType import ConfigSourceType
from orwynn.base.indication.Indication import Indication
from orwynn.boot.BootMode import BootMode


class BootConfig(Config):
    """Contains information about boot.

    Attributes:
        mode:
            Boot mode.
        root_dir:
            Root directory of the boot.
    """
    SOURCE = ConfigSource(type=ConfigSourceType.FWONLY, source="boot")

    mode: BootMode
    root_dir: str
    api_indication: Indication
