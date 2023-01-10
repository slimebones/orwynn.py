from typing import ClassVar

from orwynn.controller.MissingControllerClassAttributeError import \
    MissingControllerClassAttributeError
from orwynn.validation import validate, validate_route


class Controller:
    """Entrypoint to some operational service."""
    ROUTE: ClassVar[str | None] = None

    def __init__(self) -> None:
        if self.ROUTE is None:
            raise MissingControllerClassAttributeError(
                "you should set class attribute ROUTE for"
                f" controller {self.__class__}"
            )
        else:
            validate(self.ROUTE, str)
            validate_route(self.ROUTE)
            self.__route: str = self.ROUTE

    @property
    def route(self) -> str:
        return self.__route
