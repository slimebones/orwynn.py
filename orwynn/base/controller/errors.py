from orwynn.base.error import Error


class MissingControllerClassAttributeError(Error):
    pass


class AlreadyRegisteredMethodError(Error):
    """For the same route the method is already registered."""
