from typing import TypeVar, Union

from orwynn.base.model.model import Model

Indicatable = Union[Model, Exception]
IndicatableTypeVar = TypeVar("IndicatableTypeVar", bound=Indicatable)
