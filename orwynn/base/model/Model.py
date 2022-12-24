from typing import Any, Self, TypeVar
import pydantic

from orwynn.proxy.BootProxy import BootProxy

RecoverType = TypeVar("RecoverType", bound="Model")


class Model(pydantic.BaseModel):
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
        return BootProxy.ie().api_indication.digest(self)

    @classmethod
    def recover(cls, mp: dict) -> Self:
        """Recovers model of this class using dictionary."""
        return BootProxy.ie().api_indication.recover_model_with_type(
            cls, mp
        )

    @classmethod
    def create_dynamic(cls, name: str, **kwargs) -> type[Self]:
        return pydantic.create_model(name, __base__=cls, **kwargs)

    class Config:
        underscore_attrs_are_private = True
