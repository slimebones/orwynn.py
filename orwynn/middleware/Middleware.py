from orwynn import validation
from orwynn.middleware.NextCallFn import NextCallFn
from orwynn import web


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
            List of routes covered by this middleware. You can pass ["*"] to
            process all routes.
    """
    def __init__(self, covered_routes: list[str]) -> None:
        validation.validate_each(
            covered_routes, str, expected_sequence_type=list
        )
        self.__covered_routes: list[str] = covered_routes
        self.__is_all_routes_allowed: bool = "*" in covered_routes

        if self.__is_all_routes_allowed and len(covered_routes) != 1:
            raise ValueError(
                "if you pass \"*\" to covered routes, don't add any other"
                " values"
            )

    def __should_process(self, route: str) -> bool:
        return self.__is_all_routes_allowed or route in self.__covered_routes

    async def dispatch(
        self,
        request: web.Request,
        call_next: NextCallFn
    ) -> web.Response:
        if self.__should_process(request.url.path):
            return await self.process(request, call_next)
        else:
            return await call_next(request)

    async def process(
        self,
        request: web.Request,
        call_next: NextCallFn
    ) -> web.Response:
        raise NotImplementedError()
