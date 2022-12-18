from pathlib import Path
from orwynn.base.config.config_source.ConfigSourceType import ConfigSourceType
from orwynn.base.model.Model import Model
from orwynn.base.config.config_source.UnitedConfigSourceType import \
    UnitedConfigSourceType
from orwynn.util.validation import model_validator


class ConfigSource(Model):
    """Represents location with data config should be populated with."""
    type: ConfigSourceType | UnitedConfigSourceType
    value: str | Path | None

    @model_validator("value")
    def validate_source(cls, v, values):
        _type = values["type"]
        if type(_type) is UnitedConfigSourceType and v is not None:
            raise TypeError(
                f"got united source type and not-None value {v}"
            )
        elif _type is ConfigSourceType.PATH and not isinstance(v, Path):
            raise TypeError(
                f"got PATH source type and non-PATH value {v}"
            )

