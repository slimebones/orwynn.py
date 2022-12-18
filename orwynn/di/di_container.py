import re
from typing import TypeVar

from orwynn.base.config.Config import Config
from orwynn.base.controller.Controller import Controller
from orwynn.base.error.malfunction_error import MalfunctionError
from orwynn.base.model.Model import Model
from orwynn.di.di_object import DIObject
from orwynn.di.di_object_already_initialized_in_container_error import \
    DIObjectAlreadyInitializedInContainerError
from orwynn.di.finalized_di_container_error import FinalizedDIContainerError
from orwynn.di.is_provider import is_provider
from orwynn.di.missing_di_object_error import MissingDIObjectError
from orwynn.SUBCLASSABLE_CLASSES import SUBCLASSABLE_CLASSES
from orwynn.util.validation import validate

_InnerObj = TypeVar("_InnerObj")


class DIContainer:
    """Holds data about initialized di objects."""
    def __init__(self) -> None:
        self._data: dict[str, DIObject] = {}

        # Struct running in parallel to main data one to hold references by
        # class for self properties like getting all controllers
        self._objects_by_base_class: dict[type[DIObject], list[DIObject]] = {}

        self._is_provider_populating_finalized: bool = False

    @property
    def items(self) -> list[tuple[str, DIObject]]:
        result: list[tuple[str, DIObject]] = []

        for name, obj in self._data.items():
            result.append((name, obj))

        return result

    @property
    def controllers(self) -> list[Controller]:
        """Fetches all controllers from container.

        Returns:
            All controllers fetched.
        """
        result: list[Controller] = self._find_objects_for_class(Controller)

        return result

    def add(self, obj: DIObject) -> None:
        """Adds DI object to the container.

        Args:
            obj:
                DI object to add.

        Raises:
            DIObjectAlreadyInitializedError:
                This DI object already exists in container.
        """
        if self._is_provider_populating_finalized and is_provider(type(obj)):
            raise FinalizedDIContainerError(
                f"cannot add provider {obj}, container is finalized"
            )

        obj_class_name: str = obj.__class__.__name__

        if obj_class_name in self._data.keys():
            raise DIObjectAlreadyInitializedInContainerError(
                f"DI object {obj} already initialized"
            )

        self._data[obj_class_name] = obj

        self._assign_obj_to_base_class(obj)

    def find(self, key: str) -> DIObject:
        """Returns DI object by its key.

        Note that searching is made using PascalCased keys, but actual object
        returned is an initialized instance of searched class.

        Args:
            key:
                String value to search with.

        Returns:
            A DIObject found.

        Raises:
            MissingDIObjectError:
                DIObject with given key is not found.
        """
        validate(key, str)

        try:
            return self._data[key]
        except KeyError:
            raise MissingDIObjectError(
                f"di object for key \"{key}\" is not found"
            )

    def find_re(self, pattern: str) -> list[DIObject]:
        """Searches di objects by pattern.

        Args:
            pattern:
                Pattern to apply.

        Returns:
            All di objects with keys matched given pattern.
        """
        validate(pattern, str)

        result: list[DIObject] = []

        for k, v in self._data.items():
            if re.match(pattern, k):
                result.append(v)

        if result == []:
            raise MissingDIObjectError(
                "di objects for pattern \"pattern\" are not found"
            )

        return result

    def finalize_provider_populating(
        self
    ) -> None:
        """Finalizes the container applying logic after provider populating.
        """
        if self._is_provider_populating_finalized:
            raise ValueError("already finalized")

        self._is_provider_populating_finalized = True

    def _assign_obj_to_base_class(self, obj: DIObject) -> None:
        ObjCls: type[DIObject] = type(obj)
        BaseCls: type[DIObject] | None = None

        # Find out object's base class
        for C in SUBCLASSABLE_CLASSES:
            if issubclass(ObjCls, C):
                # Choose more specific base class Config instead of Model
                if C is Model and issubclass(ObjCls, Config):
                    BaseCls = Config
                else:
                    BaseCls = C

        if not BaseCls:
            raise MalfunctionError(
                f"cannot found base class for obj {obj}, this object"
                " shouldn't be appeared in container"
            )

        try:
            self._objects_by_base_class[BaseCls].append(obj)
        except KeyError:
            self._objects_by_base_class[BaseCls] = [obj]

    def _find_objects_for_class(self, C: type[_InnerObj]) -> list[_InnerObj]:
        result: list[_InnerObj] = []
        is_missing: bool = False

        try:
            result = self._objects_by_base_class[C]  # type: ignore
        except KeyError:
            is_missing = True
        else:
            if result == []:
                is_missing = True

        if is_missing:
            raise MissingDIObjectError(
                f"cannot find any object for class {C}"
            )
        else:
            return result
