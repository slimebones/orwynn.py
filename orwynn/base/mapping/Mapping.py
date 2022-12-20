import functools
from typing import Any, Callable
from orwynn.base.mapping.MappingNotLinkedError import MappingNotLinkedError

from orwynn.base.model.Model import Model


def if_linked(fn: Callable) -> Callable:
    @functools.wraps(fn)
    def inner(mapping: Mapping, *args, **kwargs) -> Any:
        if not mapping.is_linked:
            raise MappingNotLinkedError(
                f"{mapping} is not linked to database yet"
            )
        return fn(mapping, *args, **kwargs)
    return inner


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
