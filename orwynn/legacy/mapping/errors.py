from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from orwynn.mapping import Mapping


class MappingIdAlreadySetError(Exception):
    pass


class CustomUseOfMappingReservedFieldError(Exception):
    pass


class UnsetIdMappingError(Exception):
    """
    Id for document has not been set yet.
    """
    def __init__(
        self,
        *,
        explanation: str,
        mapping: "Mapping"
    ) -> None:
        message: str = \
            f"{explanation}: id for mapping <{mapping}> has not been set yet"
        super().__init__(message)


class MappingNotLinkedError(Exception):
    """Is mapping is not linked to accoridng object in database."""
