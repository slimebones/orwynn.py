


class MissingControllerClassAttributeError(Exception):
    pass


class AlreadyRegisteredMethodError(Exception):
    """For the same route the method is already registered."""
