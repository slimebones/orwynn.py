from typing import Any
from orwynn.base.model.Model import Model


class Mapping(Model):
    """Encapsulates logic of working with database for chosen MODEL.

    Makes a tree of other subclasses which describe interactions with certain
    database kind. End framework user should create their own Mapping
    subclasses and define MODEL and other required class attributes.
    """
    def __init__(self, **data: Any) -> None:
        super().__init__(**data)

    @classmethod
    def find_all(cls, *args, **kwargs) -> Any:
        raise NotImplementedError()

    @classmethod
    def find_one(cls, *args, **kwargs) -> Any:
        raise NotImplementedError()

    @classmethod
    def create(cls, *args, **kwargs) -> Any:
        raise NotImplementedError()

    @classmethod
    def update(cls, *args, **kwargs) -> Any:
        raise NotImplementedError()

    @classmethod
    def remove(cls, *args, **kwargs) -> Any:
        raise NotImplementedError()
