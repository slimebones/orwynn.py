from orwynn.indication.indicatable import Indicatable
from orwynn.model.model import Model


class EndpointResponse(Model):
    status_code: int
    Entity: type[Indicatable]
    description: str | None = None
