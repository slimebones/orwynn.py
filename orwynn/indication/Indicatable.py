from typing import TypeVar, Union

from orwynn.base.error.Error import Error
from orwynn.base.model.Model import Model

Indicatable = Union[Model, Error, Exception]
IndicatableTypeVar = TypeVar("IndicatableTypeVar", bound=Indicatable)
