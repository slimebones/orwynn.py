from copy import copy

from orwynn.utils import validation

from .errors import UnsupportedVersionError


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

    def apply_version_to_route(
        self,
        route: str,
        version: int | None = None
    ) -> str:
        """
        Applied a given version to a given route.

        Args:
            route:
                Route to apply version to.
            version (optional):
                Number of version to apply. By default the latest is applied.
        """
        if version is None:
            version = self.latest
        self.check_if_supported(version)

        if "{version}" not in route:
            raise ValueError(
                "no version format block in given route to insert the version"
            )

        return route.replace(
            "{version}",
            str(version)
        )

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
