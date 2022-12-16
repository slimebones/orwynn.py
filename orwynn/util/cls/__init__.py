from orwynn.util.types import Class
from orwynn.base.error.error import Error


class ClassNotFoundError(Error):
    pass


def find_subclass_by_name(name: str, BaseClass: Class) -> Class:
    """Searches given base class for subclass with given name.

    Args:
        name:
            Name of the target class.
        BaseClass:
            Where to search for subclasses.

    Returns:
        Class found.
    """
    return __traverse_subclasses_checking_name(name, BaseClass)


def __traverse_subclasses_checking_name(name: str, C: Class) -> Class:
    for SubClass in C.__subclasses__():
        if SubClass.__name__ == name:
            return SubClass
        else:
            __traverse_subclasses_checking_name(name, SubClass)

    raise ClassNotFoundError(
        f"class of supertype {C} with name {name} is not found"
    )
