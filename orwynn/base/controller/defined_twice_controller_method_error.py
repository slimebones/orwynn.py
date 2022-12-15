from orwynn.base.error.error import Error


class DefinedTwiceControllerMethodError(Error):
    """Twice defined method in Controller.METHODS, e.g.
    METHODS=["get", "post", "get", ...]
    """
    pass
