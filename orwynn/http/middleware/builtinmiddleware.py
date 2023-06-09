from orwynn.http.middleware.middleware import HttpMiddleware


class BuiltinHttpMiddleware(HttpMiddleware):
    """Special framework's middleware which covers all possible routes."""
    def __init__(self) -> None:
        # Cover all routes
        super().__init__(["*"])
