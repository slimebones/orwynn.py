from pydantic import BaseModel
from pykit.fcode import code


class DocFieldLink(BaseModel):
    target_doc: str
    target_field: str

class DocField(BaseModel):
    """
    Represents Doc field specification.
    """
    name: str
    unique: bool = False
    link: DocFieldLink | None = None

@code("unique.field.err")
class UniqueFieldErr(Exception):
    pass

