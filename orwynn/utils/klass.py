from typing import TypeVar

ClassType = TypeVar("ClassType")


class Static:
    def __init__(self) -> None:
        raise NotImplementedError(self.__class__)


def find_all_subclasses(
    Base: type[ClassType],
) -> list[type[ClassType]]:
    """
    Recursively searches for all subclasses of the base class and returns it.
    """
    Classes: list[type[ClassType]] = []

    _traverse_for_subclasses(Base, Classes)

    return Classes


def _traverse_for_subclasses(
    Start: type[ClassType],
    target_list: list[type[ClassType]],
):
    for klass in Start.__subclasses__():
        target_list.append(klass)
        _traverse_for_subclasses(klass, target_list)
