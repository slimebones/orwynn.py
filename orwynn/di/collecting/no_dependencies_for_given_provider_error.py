from orwynn.base.error.error import Error
from orwynn.di.provider import Provider


class NoDependenciesForGivenProviderError(Error):
    def __init__(
        self,
        message: str = "",
        P: type[Provider] | None = None
    ) -> None:
        if not message and P:
            message = f"{P} has no dependencies"
        super().__init__(message)
