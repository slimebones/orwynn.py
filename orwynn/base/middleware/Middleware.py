from typing import Callable
from orwynn.util import validation

from orwynn.util.http import Request, Response


class Middleware:
    """Accesses requests before they're processed and responses before
    they're returned.

    Should implement method process(...) accepting request and object of the
    next function to call. This method should always return response in either
    modified or unmodified state.

    Generally shouldn't reimplement method dispatch(...) as it's decision
    entrypoint.

    Attributes:
        covered_routes:
            List of routes covered by this middleware.
    """
    def __init__(self, covered_routes: list[str]) -> None:
        validation.validate_each(covered_routes, str, expected_obj_type=list)
        self.__covered_roures: list[str] = covered_routes

    def __should_process(self, route: str) -> bool:
        return route in self.__covered_roures

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        return await call_next(request)

    async def process(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        raise NotImplementedError()
