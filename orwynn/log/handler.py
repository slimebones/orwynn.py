from datetime import time, timedelta
from typing import Callable

from orwynn.base.model.model import Model
from orwynn.log.types import LogMessage
from orwynn.utils.types import CashOperator


class LogHandler(Model):
    # Only mattering for default values fields are added from loguru, others
    # are moved to kwargs dict. Fields set to None by default will be assigned
    # at runtime depending on some conditions
    sink: str | CashOperator | Callable[[LogMessage], None]
    level: int | str | None = None
    format: str | Callable = \
        "{time:%Y.%m.%d at %H:%M:%S.%f%z}" \
        + " | {level} | {extra} >> {message}"
    # Callable here used instead of loguru.RotationFunction since it has
    # problems with importing
    rotation: str | int | time | timedelta | Callable = "10 MB"
    serialize: bool | None = None
    kwargs: dict | None = None
