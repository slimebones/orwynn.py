import typing
from typing import Any

from orwynn.base.model.model import Model
from orwynn.mapping.errors import MappingNotLinkedError, UnsetIdMappingError
from orwynn.utils.types import TDecoratedCallable


def if_linked(
    fn: TDecoratedCallable
) -> TDecoratedCallable:
    def inner(self: Mapping, *args, **kwargs):
        if not self.is_linked:
            raise MappingNotLinkedError(
                f"{self} is not linked to database yet"
            )
        return fn(self, *args, **kwargs)
    return typing.cast(TDecoratedCallable, inner)


class Mapping(Model):
    """Encapsulates logic of working with database for chosen MODEL.

    Makes a tree of other subclasses which describe interactions with certain
    database kind. End framework user should create their own Mapping
    subclasses and define MODEL and other required class attributes.
    """
    id: str | None = None

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)

    def getid(self) -> str:
        if self.id is None:
            raise UnsetIdMappingError(
                explanation="cannot get an id",
                mapping=self
            )
        else:
            return self.id

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
