from typing import ClassVar

from orwynn import validation, web
from orwynn.error.MalfunctionError import MalfunctionError
from orwynn.web.Protocol import Protocol


class ExceptionHandler:
    """Handles outcoming errors from the application.
    Method handle(...) should be redefined in subclass in order to work.

    Class-Attributes:
        E:
            Exception or a list of handled Exceptions.
        PROTOCOL:
            Protocol the handler works with.
    """
    E: ClassVar[type[Exception] | None] = None
    PROTOCOL: Protocol = Protocol.HTTP

    def __init__(self) -> None:
        if self.E is None:
            raise TypeError(
                f"{self.__class__} error class is not set"
            )
        else:
            validation.validate(self.E, Exception)

        validation.validate(self.PROTOCOL, Protocol)

    @classmethod
    def get_handled_exception_class(cls) -> type[Exception]:
        if cls.E is None:
            raise MalfunctionError(
                f"error handler {cls} handled exception shouldn't be None"
            )
        return cls.E

    @property
    def HandledException(self) -> type[Exception]:
        return self.__class__.get_handled_exception_class()

    def handle(
        self,
        request: web.GenericRequest,
        error: Exception
    ) -> web.GenericResponse:
        raise NotImplementedError()
