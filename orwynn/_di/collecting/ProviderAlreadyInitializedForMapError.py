from orwynn._di.Provider import Provider


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
