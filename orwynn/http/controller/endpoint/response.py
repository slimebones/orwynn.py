from orwynn.base.model.model import Model
from orwynn.indication.indicatable import Indicatable


class EndpointResponse(Model):
    status_code: int
    Entity: type[Indicatable]
    description: str | None = None
