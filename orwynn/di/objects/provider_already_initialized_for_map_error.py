from orwynn.base.error.error import Error
from orwynn.di.objects.provider import Provider


class ProviderAlreadyInitializedForMapError(Error):
    def __init__(
        self, message: str = "", FailedProvider: type[Provider] | None = None
    ) -> None:
        if not message and FailedProvider:
            message = "{} already initialized for this map".format(
                FailedProvider
            )
        super().__init__(message)
