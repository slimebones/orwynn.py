from pydantic import BaseModel
from pykit.fcode import code


class DocField(BaseModel):
    """
    Represents Doc field specification.
    """
    name: str
    unique: bool = False
    linked_doc: str | None = None

@code("unique.field.err")
class UniqueFieldErr(Exception):
    pass

