from orwynn.base.service.service import Service


class RootService(Service):
    """Acts most like a generic Service, but is pre-initialized in DI.

    Shouldn't be subclassed in user's applications, only in the framework or
    extensions.
    """
    pass
