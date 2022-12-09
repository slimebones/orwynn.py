from typing import Any
from orwynn.base.model.model import Model


class Cell(Model):
    """Special model to store an abstraction of a database object."""
    id: str
    type: type[Any] 