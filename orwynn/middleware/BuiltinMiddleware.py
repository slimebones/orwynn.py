from orwynn.middleware.Middleware import Middleware


class BuiltinMiddleware(Middleware):
    """Special framework's middleware which covers all possible routes."""
    def __init__(self) -> None:
        # Cover all routes
        super().__init__(["*"])
