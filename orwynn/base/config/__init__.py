from pathlib import Path
from typing import Any, TypeVar

from orwynn.base.config.Config import Config
from orwynn.base.config.config_source.ConfigSource import ConfigSource
from orwynn.base.config.config_source.ConfigSourceType import ConfigSourceType
from orwynn.base.config.config_source.UnitedConfigSourceType import \
    UnitedConfigSourceType
from orwynn.base.config.UnknownConfigSourceError import \
    UnknownConfigSourceError
from orwynn.boot.BootDataProxy import BootDataProxy
from orwynn.di.provider import Provider
from orwynn.util import validation
from orwynn.util.file.yml import load_yml

CreatedConfig = TypeVar("CreatedConfig", bound=Config)


def fw_create_config(
    C: type[CreatedConfig],
    **provider_kwargs: dict[str, Provider]
) -> CreatedConfig:
    """Creates config parsing SOURCE and injecting providers.

    Called only by framework's workers.

    Attributes:
        **provider_kwargs:
            Provider by its expected name as in config's attributes.

    Returns:
        Initialized config instance.

    Raises:
        UnsupportedConfigSourceError:
            SOURCE = "boot" can be used only by framework.
        UnsupportedConfigSourceError:
            Config source wasn't recognized.
    """
    if not C.SOURCE:
        raise UnknownConfigSourceError(
            f"config {C} should define SOURCE class attribute"
        )
    source_kwargs: dict[str, Any] = _load_source(C.__name__, C.SOURCE)
    return C(**source_kwargs, **provider_kwargs)


def _load_source(
    config_name: str,
    source: ConfigSource
) -> dict[str, Any]:
    result: dict[str, Any] = {}

    if type(source.type) is ConfigSourceType:
        if (
            source.type is ConfigSourceType._FWONLY
            and source.value == "boot"
        ):
            if config_name != "BootConfig":
                raise UnknownConfigSourceError(
                    "SOURCE=\"boot\" can be used only by framework"
                )
            return BootDataProxy.ie().data
        elif source.type is ConfigSourceType.PATH:
            result = load_yml(validation.apply(source.value, Path))
        else:
            raise UnknownConfigSourceError(
                f"unknown source type {source.type}"
            )
    elif type(source.type) is UnitedConfigSourceType:
        pass
    else:
        raise UnknownConfigSourceError(
            f"unknown source type {source.type}"
        )

    return result
