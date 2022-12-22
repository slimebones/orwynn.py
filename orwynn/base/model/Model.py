from typing import Any, Self, TypeVar
from pydantic import BaseModel

from orwynn.boot._BootDataProxy import BootDataProxy

RecoverType = TypeVar("RecoverType", bound="Model")


class Model(BaseModel):
    """Basic way to represent a data in the app."""
    def __init__(self, **data: Any) -> None:
        super().__init__(**data)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({super().__str__()})"

    @property
    def api(self) -> dict:
        """Generates API-complying object using project's defined API
        indication.
        """
        return BootDataProxy.ie().api_indication.digest(self)

    @classmethod
    def recover(cls, mp: dict) -> Self:
        """Recovers model of this class using dictionary."""
        return BootDataProxy.ie().api_indication.recover_model_with_type(
            cls, mp
        )

    class Config:
        underscore_attrs_are_private = True
