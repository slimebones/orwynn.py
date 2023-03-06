


class MappingIdAlreadySetError(Exception):
    pass


class CustomUseOfMappingReservedFieldError(Exception):
    pass


class MappingIdNotSetError(Exception):
    pass


class MappingNotLinkedError(Exception):
    """Is mapping is not linked to accoridng object in database."""
