from typing import Any, ClassVar, Literal, Self
from orwynn.base.config.config_source.ConfigSource import ConfigSource
from orwynn.base.config.config_source.ConfigSourceType import ConfigSourceType
from orwynn.base.config.config_source.UnitedConfigSourceType import UnitedConfigSourceType

from orwynn.base.config.UnknownConfigSourceError import \
    UnknownConfigSourceError
from orwynn.base.model.Model import Model
from orwynn.boot.BootDataProxy import BootDataProxy
from orwynn.di.provider import Provider
from orwynn.util.validation import is_path
from orwynn.util.file.yml import load_yml


class Config(Model):
    """Object holding configuration which can be injected to any requesting
    entity.

    Config is a Provider and has highest priority to be initialized in DI
    chain, so it makes it a perfect candidate to be requested in other entities
    as a configuration model.

    Every config should define class attribute SOURCE indicates the source to
    load configuration fields from.

    Note that fields which is not in Providers group, are injected via DI,
    others are searched in given SOURCE.
    """
    SOURCE: ClassVar[ConfigSource] = ConfigSource(
        type=UnitedConfigSourceType.UNITED_PATH,
        value=None
    )

    class Config:
        arbitrary_types_allowed = True
