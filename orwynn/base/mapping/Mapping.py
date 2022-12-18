from typing import Any
from orwynn.base.mapping.UndefinedMappingModelError import \
    UndefinedMappingModelError
from orwynn.base.model.Model import Model
from orwynn.util.validation import validate


class Mapping:
    """Encapsulates logic of working with database for chosen MODEL.

    Makes a tree of other subclasses which describe interactions with certain
    database kind. End framework user should create their own Mapping
    subclasses and define MODEL and other required class attributes.
    """
    MODEL: type[Model] | None = None

    def __init__(self) -> None:
        if self.MODEL is None:
            raise UndefinedMappingModelError(
                f"define MODEL attribute for mapping {self.__class__}"
            )
        else:
            validate(self.MODEL, Model)
            self.__MODEL: type[Model] = self.MODEL

    def find_all(self, *args, **kwargs) -> Any:
        raise NotImplementedError()

    def find_one(self, *args, **kwargs) -> Any:
        raise NotImplementedError()

    def create(self, *args, **kwargs) -> Any:
        raise NotImplementedError()

    def update(self, *args, **kwargs) -> Any:
        raise NotImplementedError()

    def remove(self, *args, **kwargs) -> Any:
        raise NotImplementedError()
