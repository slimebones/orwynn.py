import functools
from typing import Any, Callable

from orwynn.utils.types import Class

from .errors import ClassNotFoundError


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
    # Maybe given class has correct name
    if BaseClass.__name__ == name:
        return BaseClass

    out: Class | None = __traverse_subclasses_checking_name(name, BaseClass)

    if out is None:
        raise ClassNotFoundError(
            f"class of supertype {BaseClass} with name {name} is not found"
        )
    else:
        return out

def bind_first_arg(arg: Any):
    """Adds first argument to wrapped function call.

    Useful when you want to add e.g. "self" with some instance to dynamically
    obtained class's method.

    Args:
        arg:
            First arg to be added to wrapped function call.

    Returns:
        Wrapper accepting function.
    """
    def wrapper(fn: Callable):
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            return fn(arg, *args, **kwargs)
        return inner
    return wrapper


def bind_first_arg_async(arg: Any):
    """Same as bind_first_arg(), but for async functions.
    """
    def wrapper(fn: Callable):
        @functools.wraps(fn)
        async def inner(*args, **kwargs):
            return await fn(arg, *args, **kwargs)
        return inner
    return wrapper


def __traverse_subclasses_checking_name(name: str, C: Class) -> Class | None:
    for SubClass in C.__subclasses__():
        if SubClass.__name__ == name:
            return SubClass
        else:
            result: Class | None = \
                __traverse_subclasses_checking_name(name, SubClass)
            if result is not None:
                return result

    return None
