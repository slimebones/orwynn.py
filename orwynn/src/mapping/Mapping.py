import typing
from typing import Any

from orwynn.src.mapping.MappingNotLinkedError import MappingNotLinkedError
from orwynn.src.model.Model import Model
from orwynn.src.types import DecoratedCallable


def if_linked(
    fn: DecoratedCallable
) -> DecoratedCallable:
    def inner(self: Mapping, *args, **kwargs):
        if not self.is_linked:
            raise MappingNotLinkedError(
                f"{self} is not linked to database yet"
            )
        return fn(self, *args, **kwargs)
    return typing.cast(DecoratedCallable, inner)


class Mapping(Model):
    """Encapsulates logic of working with database for chosen MODEL.

    Makes a tree of other subclasses which describe interactions with certain
    database kind. End framework user should create their own Mapping
    subclasses and define MODEL and other required class attributes.
    """
    id: str | None = None

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)

    def is_linked(self) -> bool:
        """Whether this mapping is linked to actual object in database.
        """
        return self.id is not None

    @classmethod
    def find_all(cls, *args, **kwargs) -> Any:
        raise NotImplementedError()

    @classmethod
    def find_one(cls, *args, **kwargs) -> Any:
        raise NotImplementedError()

    def create(self, *args, **kwargs) -> Any:
        raise NotImplementedError()

    def update(self, *args, **kwargs) -> Any:
        raise NotImplementedError()

    def remove(self, *args, **kwargs) -> Any:
        raise NotImplementedError()
