import re
from types import NoneType
from typing import ClassVar, Literal

from orwynn.base.controller.errors import (
    MissingControllerClassAttributeError,
)
from orwynn.utils import validation
from orwynn.utils.url import match_routes


class Controller:
    """Entrypoint to some operational service."""
    ROUTE: ClassVar[str | None] = None
    VERSION: ClassVar[int | set[int] | Literal["*"] | None] = None

    def __init__(self) -> None:
        # Actual route for the controller assigned at boottime
        self._final_routes: set[str] | None = None

        if self.ROUTE is None:
            raise MissingControllerClassAttributeError(
                "you should set class attribute ROUTE for"
                f" controller {self.__class__}"
            )
        else:
            validation.validate(self.ROUTE, str)
            validation.validate_route(self.ROUTE)
            self._route: str = self.ROUTE

        validation.validate(self.VERSION, [int, set, str, NoneType])
        if isinstance(self.VERSION, str) and self.VERSION != "*":
            raise TypeError(
                f"unrecognized VERSION {self.VERSION}"
            )

    @property
    def final_routes(self) -> set[str]:
        if self._final_routes is None:
            raise ValueError(
                "final routes is not set for this controller"
            )
        return self._final_routes.copy()

    @property
    def route(self) -> str:
        return self._route

    def is_matching_route(self, real_route: str) -> bool:
        """
        Checks if given real route is matching any of controller's final
        abstract routes.

        Args:
            real_route:
                Real route with all placement blocks filled.

        Returns:
            Boolean flag.
        """
        for abstract_route in self.final_routes:
            match_result: re.Match | None = match_routes(
                abstract_route=abstract_route,
                real_route=real_route
            )

            if match_result is not None:
                return True

        return False

    def _fw_set_final_routes(self, value: set[str]) -> None:
        if self._final_routes is not None:
            raise ValueError("final route already set")
        self._final_routes = value
