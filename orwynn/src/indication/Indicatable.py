from typing import TypeVar, Union

from orwynn.src.error.Error import Error
from orwynn.src.model.Model import Model

Indicatable = Union[Model, Error, Exception]
IndicatableTypeVar = TypeVar("IndicatableTypeVar", bound=Indicatable)
