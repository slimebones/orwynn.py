from enum import Enum
from typing import Any
from peewee import CharField
from orwynn import validation
class EnumField(CharField):
    """Be able to store Enum in database as chars.

    Enum's key is actually stored since it's always convertable to string.
    """
    def __init__(self, E: type[Enum], *args: Any, **kwargs: Any) -> None:
        validation.validate(E, Enum)
        self.__Enum: type[Enum] = E
        super().__init__(*args, **kwargs)

    def db_value(self, value: Enum) -> str:
        return value.name

    def python_value(self, value: str) -> Enum:
        # Since the value is enum.name, we have to find according enum's value
        # for this name in target Enum.
        for x in self.__Enum:
            if x.name == value:
                return self.__Enum(x.value)
        raise ValueError(
            "unrecognized enum name coming from database"
            f" field: {value}"
        )
