from orwynn.base.error.error import Error


class IncorrectRouteError(Error):
    """When given route was built incorrectly.
    
    Attributes:
        message (optional):
            Message to be attached to the error.
        failed_route (optional):
            Route didn't passed checks to format a message.   
    """
    def __init__(self, message: str = "", failed_route: str = "") -> None:
        if not message and failed_route:
            message = "{} is an incorrect route".format(failed_route)

        super().__init__(message)