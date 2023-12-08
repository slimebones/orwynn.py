class CircularDependencyError(Exception):
    pass


class FrameworkServiceModuleReferenceError(Exception):
    pass


class EmptyRouteError(Exception):
    def __init__(self, message: str = "") -> None:
        if not message:
            message = "route cannot be empty"
        super().__init__(message)
