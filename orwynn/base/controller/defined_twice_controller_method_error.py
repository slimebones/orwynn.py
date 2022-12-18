from orwynn.base.error import Error


class DefinedTwiceControllerMethodError(Error):
    """Twice defined method in Controller.METHODS, e.g.
    METHODS=["get", "post", "get", ...]
    """
    pass
