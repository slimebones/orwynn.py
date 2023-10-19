import functools
from typing import Any, Callable

from orwynn.utils.types import TClass

from .errors import ClassNotFoundError


class Static:
    def __init__(self) -> None:
        raise NotImplementedError


class ClassUtils(Static):
    @classmethod
    def find_all_subclasses(
        cls,
        Base: type[TClass],
    ) -> list[type[TClass]]:
        """
        Recursively searches for all subclasses of the base class and returns
        it.
        """
        Classes: list[type[TClass]] = []

        cls._traverse_for_subclasses(Base, Classes)

        return Classes

    @classmethod
    def _traverse_for_subclasses(
        cls,
        Start: type[TClass],
        target_list: list[type[TClass]],
    ):
        for klass in Start.__subclasses__():  # type: ignore
            target_list.append(klass)
            cls._traverse_for_subclasses(klass, target_list)

    @classmethod
    def find_subclass_by_name(cls, name: str, BaseClass: TClass) -> TClass:
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

        out: TClass | None = cls._traverse_subclasses_checking_name(
            name, BaseClass
        )

        if out is None:
            raise ClassNotFoundError(
                f"class of supertype {BaseClass} with name {name} is not found"
            )
        else:
            return out

    @classmethod
    def bind_first_arg(cls, arg: Any):
        """Adds first argument to wrapped function call.

        Useful when you want to add e.g. "self" with some instance to
        dynamically obtained class's method.

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

    @classmethod
    def bind_first_arg_async(cls, arg: Any):
        """Same as bind_first_arg(), but for async functions.
        """
        def wrapper(fn: Callable):
            @functools.wraps(fn)
            async def inner(*args, **kwargs):
                return await fn(arg, *args, **kwargs)
            return inner
        return wrapper

    @classmethod
    def _traverse_subclasses_checking_name(
        cls,
        name: str,
        C: TClass
    ) -> TClass | None:
        for SubClass in C.__subclasses__():
            if SubClass.__name__ == name:
                return SubClass
            else:
                result: TClass | None = \
                    cls._traverse_subclasses_checking_name(name, SubClass)
                if result is not None:
                    return result

        return None
