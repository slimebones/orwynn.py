from datetime import time, timedelta
from typing import Any, Callable

from orwynn.model.Model import Model


class LogHandler(Model):
    # Only mattering for default values fields are added from loguru, others
    # are moved to kwargs dict. Fields set to None by default will be assigned
    # at runtime depending on some conditions
    sink: Any
    level: int | str | None = None
    format: str | Callable = \
        "{time:%Y.%m.%d at %H:%M:%S.%f%z}" \
        + " | {level} | {extra} >> {message}"
    # Callable here used instead of loguru.RotationFunction since it has
    # problems with importing
    rotation: str | int | time | timedelta | Callable = "10 MB"
    serialize: bool | None = None
    kwargs: dict
