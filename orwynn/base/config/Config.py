import re
from typing import Any, Self
from orwynn.base.model.Model import Model
from orwynn.app_rc.AppRC import AppRC
from orwynn.boot._BootProxy import BootProxy
from orwynn.util import validation


class Config(Model):
    """Object holding configuration which can be injected to any requesting
    entity.
    """
    @classmethod
    def load(cls, *, extra: dict[str, Any] | None = None) -> Self:
        if not extra:
            extra = {}

        validation.validate_dict(extra, (str, validation.Validator.SKIP))

        app_rc: AppRC = BootProxy.ie().app_rc
        config_kwargs: dict[str, Any] = app_rc.get(
            cls._convert_name_to_rc_format(),
            {}
        )
        return cls(**validation.apply(config_kwargs, dict), **extra)

    @classmethod
    def _convert_name_to_rc_format(cls) -> str:
        cleaned_name: str = cls.__name__
        if re.match(r"^.+config$", cls.__name__.lower()):
            cleaned_name = cls.__name__[:len(cls.__name__) - 6]
        return cleaned_name

    class Config:
        arbitrary_types_allowed = True
