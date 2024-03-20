from fcode import code
from pydantic import BaseModel


class DocField(BaseModel):
    """
    Represents Doc field specification.
    """

    name: str
    unique: bool = False


@code("unique.field.err")
class UniqueFieldErr(Exception):
    pass

