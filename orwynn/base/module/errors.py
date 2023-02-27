from orwynn.base.error import Error


class FrameworkServiceModuleReferenceError(Error):
    pass


class EmptyRouteError(Error):
    def __init__(self, message: str = "") -> None:
        if not message:
            message = "route cannot be empty"
        super().__init__(message)
