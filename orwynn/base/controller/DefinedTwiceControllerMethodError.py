from orwynn.base.error._Error import Error


class DefinedTwiceControllerMethodError(Error):
    """Twice defined method in Controller.METHODS, e.g.
    METHODS=["get", "post", "get", ...]
    """
    pass
