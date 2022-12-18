from typing import Any, ClassVar, Literal, Self
from orwynn.base.config.config_source.ConfigSource import ConfigSource
from orwynn.base.config.config_source.ConfigSourceType import ConfigSourceType

from orwynn.base.config.unsupported_config_source_error import \
    UnsupportedConfigSourceError
from orwynn.base.model.Model import Model
from orwynn.boot.BootDataProxy import BootDataProxy
from orwynn.di.provider import Provider
from orwynn.util.file.is_path import is_path
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
        type=ConfigSourceType.UNITED_PATH,
        source=None
    )

    @classmethod
    def fw_create(
        cls: type[Self],
        provider_kwargs: dict[str, Provider]
    ) -> Self:
        """Creates config parsing SOURCE and injecting providers.

        Called only by framework's workers.

        Attributes:
            provider_kwargs:
                Dict of provider by its expected name as an config's attribute.

        Returns:
            Initialized config instance.

        Raises:
            UnsupportedConfigSourceError:
                SOURCE = "boot" can be used only by framework.
            UnsupportedConfigSourceError:
                Config source wasn't recognized.
        """
        if not cls.SOURCE:
            raise UnsupportedConfigSourceError(
                f"config {cls} should define SOURCE class attribute"
            )
        source_kwargs: dict[str, Any] = cls._load_source(cls.SOURCE)
        return cls(**source_kwargs, **provider_kwargs)

    @classmethod
    def _load_source(cls, source: ConfigSource) -> dict[str, Any]:
        result: dict[str, Any] = {}

        if (
            source.type is ConfigSourceType.FWONLY
            and source.source == "boot"
        ):
            if cls.__name__ != "BootConfig":
                raise UnsupportedConfigSourceError(
                    "SOURCE=\"boot\" can be used only by framework"
                )
            return BootDataProxy.ie().data

        elif is_path(source.source):
            result = load_yml(source)  # type: ignore
        else:
            raise NotImplementedError(
                "non-Path sources are not supported in this version"
            )

        return result

    class Config:
        arbitrary_types_allowed = True
