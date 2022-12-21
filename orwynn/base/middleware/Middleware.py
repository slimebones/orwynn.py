from typing import Callable
from orwynn.util.http import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class Middleware(BaseHTTPMiddleware):
    """Accesses requests before they're processed and responses before
    they're returned.

    Should implement method `dispatch` accepting request and object of the next
    function to call. This method should always return response in either
    modified or unmodified state.
    """
    def __init__(self, *args) -> None:
        pass

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        raise NotImplementedError()
