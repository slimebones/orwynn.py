from orwynn.di.object import DiObject
from orwynn.di.provider import Provider


class MissingDiObjectError(Exception):
    pass


class FinalizedDiContainerError(Exception):
    """If some evil force is trying to add objects to a finalized container.
    """


class DiObjectAlreadyInitializedInContainerError(Exception):
    """DI object has been already initialized.
    """


class NoAnnotationError(Exception):
    """If di object has attribute without annotation."""



class NotProviderError(Exception):
    def __init__(
        self,
        message: str = "",
        FailedClass: type | None = None
    ) -> None:
        if not message and FailedClass:
            message = "{} is not a Provider".format(FailedClass)
        super().__init__(message)


class ProviderAvailabilityError(Exception):
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
