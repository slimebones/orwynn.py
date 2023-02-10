from typing import TypeVar, Union

from orwynn.error.Error import Error
from orwynn.model.Model import Model

Indicatable = Union[Model, Error, Exception]
IndicatableTypeVar = TypeVar("IndicatableTypeVar", bound=Indicatable)
