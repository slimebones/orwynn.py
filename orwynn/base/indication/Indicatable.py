import pydantic
from orwynn.base.error.Error import Error
from orwynn.base.model.Model import Model


IndicatableClass = \
    type[Model] \
    | type[Error] \
    | type[Exception] \
    | type[pydantic.ValidationError]
Indicatable = Model | Error | Exception
