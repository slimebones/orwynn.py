from orwynn.base.indication.Indicatable import IndicatableClass
from orwynn.base.model.Model import Model


class EndpointResponse(Model):
    status_code: int
    Entity: IndicatableClass
    description: str | None = None
