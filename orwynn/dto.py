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

TUdto = TypeVar("TUdto", bound=Udto)

