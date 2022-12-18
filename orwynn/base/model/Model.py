from typing import Any, Self, TypeVar
from pydantic import BaseModel

from orwynn.boot.BootDataProxy import BootDataProxy
from orwynn.util.rnd import makeid

RecoverType = TypeVar("RecoverType", bound="Model")


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

    @classmethod
    def recover(cls, mp: dict) -> Self:
        """Recovers model of this class using dictionary."""
        return BootDataProxy.ie().api_indication.recover_model_with_type(
            cls, mp
        )
