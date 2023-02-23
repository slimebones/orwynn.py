from types import NoneType
from typing import ClassVar, Literal

from orwynn.util import validation
from orwynn.base.controller.MissingControllerClassAttributeError import (
    MissingControllerClassAttributeError,
)


class Controller:
    """Entrypoint to some operational service."""
    ROUTE: ClassVar[str | None] = None
    VERSION: ClassVar[int | set[int] | Literal["*"] | None] = None

    def __init__(self) -> None:
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
    def route(self) -> str:
        return self._route
