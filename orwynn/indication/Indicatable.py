import pydantic

from orwynn.error.Error import Error
from orwynn.model.Model import Model

IndicatableClass = \
    type[Model] \
    | type[Error] \
    | type[Exception] \
    | type[pydantic.ValidationError]
Indicatable = Model | Error | Exception
