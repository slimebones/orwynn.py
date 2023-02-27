from typing import TypeVar, Union

from orwynn.base.error import Error
from orwynn.base.model._Model import Model

Indicatable = Union[Model, Error, Exception]
IndicatableTypeVar = TypeVar("IndicatableTypeVar", bound=Indicatable)
