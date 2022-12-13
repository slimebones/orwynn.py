from orwynn.base.error.error import Error
from orwynn.di.di_object.provider import Provider


class NoDependenciesForGivenProvider(Error):
    def __init__(
        self,
        message: str = "",
        P: type[Provider] | None = None
    ) -> None:
        if not message and P:
            message = f"{P} has no dependencies"
        super().__init__(message)
