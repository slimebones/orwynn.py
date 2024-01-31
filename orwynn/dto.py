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

class Cdto(Dto):
    """
    @abs
    """
    units: list[Udto]

