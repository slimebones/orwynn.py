from pydantic import BaseModel
from typing import TypeVar
from pydantic import BaseModel


class Dto(BaseModel):
    """
    @abs
    """

class Udto(Dto):
    """
    @abs
    """
    sid: str

class Fdto(Udto):
    """
    Expanded udto where all sids (or most of them) are replaced by actual docs.

    @abs
    """

TDto = TypeVar("TDto", bound=Dto)
TUdto = TypeVar("TUdto", bound=Udto)
TFdto = TypeVar("TFdto", bound=Fdto)

class Flag(BaseModel):
    val: bool

    @staticmethod
    def code():
        return "orwynn::flag"

