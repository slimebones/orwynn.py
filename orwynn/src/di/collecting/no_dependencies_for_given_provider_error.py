from orwynn.src.di.Provider import Provider
from orwynn.src.error.Error import Error


class NoDependenciesForGivenProviderError(Error):
    def __init__(
        self,
        message: str = "",
        P: type[Provider] | None = None
    ) -> None:
        if not message and P:
            message = f"{P} has no dependencies"
        super().__init__(message)