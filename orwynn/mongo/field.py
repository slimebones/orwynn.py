from pydantic import BaseModel
from pykit.fcode import code


class DocField(BaseModel):
    """
    Represents Doc field specification.
    """

    name: str
    unique: bool = False


@code("unique.field.err")
class UniqueFieldErr(Exception):
    pass

