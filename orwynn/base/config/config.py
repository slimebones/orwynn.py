from typing import Any, ClassVar, Self

from orwynn.base.config.undefined_config_source_error import \
    UndefinedConfigSourceError
from orwynn.base.model.model import Model
from orwynn.di.provider import Provider
from orwynn.util.file.is_path import is_path
from orwynn.util.file.yml import load_yml
from orwynn.util.types import Source


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
    SOURCE: ClassVar[Source | None] = None

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
        """
        if not cls.SOURCE:
            raise UndefinedConfigSourceError(
                f"config {cls} should define SOURCE class attribute"
            )
        source_kwargs: dict[str, Any] = cls._load_source(cls.SOURCE)
        return cls(**source_kwargs, **provider_kwargs)

    @staticmethod
    def _load_source(source: Source) -> dict[str, Any]:
        result: dict[str, Any] = {}

        if is_path(source):
            result = load_yml(source)  # type: ignore
        else:
            raise NotImplementedError(
                "non-Path sources are not supported in this version"
            )

        return result
