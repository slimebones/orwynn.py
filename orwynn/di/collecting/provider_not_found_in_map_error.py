from orwynn.base.error.error import Error
from orwynn.di.provider import Provider


class ProviderNotFoundInMapError(Error):
    """If some requested provider not found in some metamap."""
    def __init__(
        self,
        message: str = "",
        P: type[Provider] | None = None
    ) -> None:
        if not message and P:
            message = f"{P} not found in map"
        super().__init__(message)
