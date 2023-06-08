from orwynn.base.service.service import Service


class FrameworkService(Service):
    """Acts most like a generic Service, but is pre-initialized in DI.

    Shouldn't be subclassed in user's applications, only in the framework or
    extensions.

    This service shouldn't be added in module.Providers in order to be
    injected - it is always accessible for any Acceptor in the app.
    """
