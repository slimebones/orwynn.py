from orwynn.di.di_object import DIObject
from orwynn.di.di_object_already_initialized_in_container_error \
    import \
    DIObjectAlreadyInitializedInContainerError
from orwynn.di.missing_di_object_error import MissingDIObjectError
from orwynn.validation import validate


class DIContainer:
    """Holds data about initialized di objects."""
    def __init__(self) -> None:
        self._data: dict[str, DIObject] = {}

    @property
    def items(self) -> list[tuple[str, DIObject]]:
        result: list[tuple[str, DIObject]] = []

        for name, obj in self._data.items():
            result.append((name, obj))

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
        obj_class_name: str = obj.__class__.__name__

        if obj_class_name in self._data.keys():
            raise DIObjectAlreadyInitializedInContainerError(
                f"DI object {obj} already initialized"
            )

        self._data[obj_class_name] = obj

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
