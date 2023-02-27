from orwynn.base.error import Error


class MappingIdAlreadySetError(Error):
    pass


class CustomUseOfMappingReservedFieldError(Error):
    pass


class MappingIdNotSetError(Error):
    pass


class MappingNotLinkedError(Error):
    """Is mapping is not linked to accoridng object in database."""
