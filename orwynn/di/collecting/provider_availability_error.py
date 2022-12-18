from orwynn.base.error.Error import Error
from orwynn.di.provider import Provider


class ProviderAvailabilityError(Error):
    """If some Provider2 is not visible for some Provider1."""
    def __init__(
        self,
        message: str = "",
        Provider1: type[Provider] | None = None,
        Provider2: type[Provider] | None = None
    ) -> None:
        if not message and Provider1 and Provider2:
            message = "provider {} is not available for {}".format(
                Provider2, Provider1
            )
        super().__init__(message)
