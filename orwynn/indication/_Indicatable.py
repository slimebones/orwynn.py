from typing import TypeVar, Union

from orwynn.base.model._Model import Model

Indicatable = Union[Model, Exception]
IndicatableTypeVar = TypeVar("IndicatableTypeVar", bound=Indicatable)
