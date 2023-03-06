from orwynn._di.Provider import Provider


class NoDependenciesForGivenProviderError(Exception):
    def __init__(
        self,
        message: str = "",
        P: type[Provider] | None = None
    ) -> None:
        if not message and P:
            message = f"{P} has no dependencies"
        super().__init__(message)
