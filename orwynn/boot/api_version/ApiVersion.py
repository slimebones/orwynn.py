from copy import copy

from orwynn import validation
from orwynn.boot.api_version.UnsupportedVersionError import (
    UnsupportedVersionError,
)


class ApiVersion:
    """Describes project's API versioning rules.

    Attributes:
        supported (optional):
            Set of version numbers supported. Defaults to only one supported
            version v1.
    """
    def __init__(
        self,
        supported: set[int] | None = None
    ) -> None:
        if supported is None:
            supported = {1}
        validation.validate_each(supported, int, expected_sequence_type=set)
        self.__supported: set[int] = supported

    @property
    def supported(self) -> set[int]:
        return copy(self.__supported)

    @property
    def latest(self) -> int:
        return max(self.__supported)

    def check_if_supported(self, version: int) -> None:
        """Checks if a version is supported.

        Raises:
            UnsupportedVersionError:
                The given version is not supported.
        """
        validation.validate(version, int)
        if version not in self.__supported:
            raise UnsupportedVersionError(
                f"version {version} is not supported"
            )
