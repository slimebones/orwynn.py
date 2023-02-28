
from orwynn.base.model._Model import Model
from orwynn.indication._Indicatable import Indicatable


class EndpointResponse(Model):
    status_code: int
    Entity: type[Indicatable]
    description: str | None = None
