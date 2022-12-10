from orwynn.base.error.error import Error


class EmptyRouteError(Error):
    def __init__(self, message: str = "") -> None:
        if not message:
            message = "route cannot be empty"
        super().__init__(message)