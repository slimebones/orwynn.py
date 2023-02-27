from orwynn._di.DiObject import DiObject
from orwynn._di.Provider import Provider
from orwynn.base.error import Error


class ProviderAvailabilityError(Error):
    """If some Provider is not visible for some other Di object."""
    def __init__(
        self,
        message: str = "",
        Provider1: type[Provider] | None = None,
        DiObject: type[DiObject] | None = None
    ) -> None:
        if not message and Provider1 and DiObject:
            message = "provider {} is not available for di object {}".format(
                DiObject, Provider1
            )
        super().__init__(message)
