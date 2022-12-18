from typing import Any
from pydantic import BaseModel

from orwynn.boot.BootDataProxy import BootDataProxy
from orwynn.util.rnd.makeid import makeid


class Model(BaseModel):
    """Basic way to represent a data in the app."""
    id: str | None = None

    def __init__(self, **data: Any) -> None:
        if "id" not in data:
            data["id"] = makeid()
        super().__init__(**data)

    @property
    def api(self) -> dict:
        """Generates API-complying object using project's defined API
        indication.
        """
        return BootDataProxy.ie().api_indication.digest_model(self)
