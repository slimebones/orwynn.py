from orwynn.di.provider import Provider


class ProviderAlreadyInitializedForMapError(Exception):
    """If provider already initialized in some metamap."""
    def __init__(
        self, message: str = "", FailedProvider: type[Provider] | None = None
    ) -> None:
        if not message and FailedProvider:
            message = "{} already initialized for this map".format(
                FailedProvider
            )
        super().__init__(message)


class ProviderNotFoundInMapError(Exception):
    """If some requested provider not found in some metamap."""
    def __init__(
        self,
        message: str = "",
        P: type[Provider] | None = None
    ) -> None:
        if not message and P:
            message = f"{P} not found in map"
        super().__init__(message)


class ProviderKeywordAttributeError(Exception):
    """
    Providers cannot have keyword-only attributes, it's not logical for DI.
    """


class NoDependenciesForGivenProviderError(Exception):
    def __init__(
        self,
        message: str = "",
        P: type[Provider] | None = None
    ) -> None:
        if not message and P:
            message = f"{P} has no dependencies"
        super().__init__(message)

