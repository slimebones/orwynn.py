from typing import Callable
from orwynn.util.request import Request
from orwynn.util.response import Response


class Middleware:
    """Accesses requests before they're processed and also responses before
    they're returned.

    Should implement method `process` accepting request and object of the next
    function to call. This method should always return response in either
    modified or unmodified state.
    """
    def __init__(self, *args) -> None:
        pass

    def process(self, request: Request, call_next: Callable) -> Response:
        raise NotImplementedError()
