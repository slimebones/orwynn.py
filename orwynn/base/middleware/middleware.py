import re
from typing import Any, Callable

from orwynn.utils import validation


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
        self._covered_routes: list[str] = covered_routes
        self.__is_all_routes_allowed: bool = "*" in covered_routes

        if self.__is_all_routes_allowed and len(covered_routes) != 1:
            raise ValueError(
                "if you pass \"*\" to covered routes, don't add any other"
                " values"
            )

    def __should_process(self, route: str) -> bool:
        if self.__is_all_routes_allowed:
            return True

        for allowed_route in self._covered_routes:
            # FIXME: Here in routes other regex-incompatible symbols may
            #   appear, but i don't know which ones at this point. Maybe we
            #   should add more advanced adjustments (replacements) or error
            #   raising.
            #
            # Replace variable brackets and dashes from kebab-style notations.
            #
            # Also, notice that for paths like "/users/10ci/...." allowed route
            # "/users/{id}" will be also compliant, which may not seemed right
            # but due to external checks before route processed to middleware
            # such types of routes won't appear here (i.e. "/users/10ci/foo"
            # won't be passed to the controller "/users/{id}").
            prepared_route: str = re.sub(
                r"\{.+\}", ".+", allowed_route
            ).replace(
                "-", r"\-"
            )

            route_pattern: re.Pattern = re.compile(
                # This way paths will be covered too -
                # e.g. "/file/{}" matches "/file/home/alex/..."
                prepared_route
            )

            if route_pattern.fullmatch(route):
                return True

        return False

    async def dispatch(
        self,
        request: Any,
        call_next: Callable
    ) -> Any:
        if self.__should_process(request.url.path):
            return await self.process(request, call_next)
        else:
            return await call_next(request)

    async def process(
        self,
        request: Any,
        call_next: Any
    ) -> Any:
        return await call_next(request)
