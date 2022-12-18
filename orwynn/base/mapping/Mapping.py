from orwynn.base.database.DatabaseService import DatabaseService
from orwynn.base.mapping.UndefinedMappingModelError import \
    UndefinedMappingModelError
from orwynn.base.model.Model import Model
from orwynn.util.validation import validate


class Mapping:
    """Encapsulates logic of working with database for chosen MODEL.

    This is an abstract class and makes a tree of other abstract subclasses
    which describe interactions with certain database kind. End framework user
    should create their own Mapping subclasses and define there MODEL and other
    required class attributes.
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
