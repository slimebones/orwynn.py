from typing import Any, ClassVar

from orwynn.model.Model import Model
from orwynn.util import validation
from orwynn.util.web import Request, Response


class ErrorHandler(Model):
    """Handles outcoming errors from the application.

    Method handle(...) should be redefined in subclass in order to work.

    Do not pass default exception to handle, since Starlette threated it
    different. If you want to handle all Exceptions, consider adding list of
    Exception.__subclasses__().
    """
    E: ClassVar[type[Exception] | list[type[Exception]] | None] = None

    def __init__(self, **data: Any) -> None:
        if self.E is None:
            raise TypeError(
                f"{self.__class__} error class is not set"
            )
        elif self.E is Exception:
            raise TypeError(
                f"{self.__class__} defines basic Exception as handled error,"
                " which is not supported, consider using"
                " Exception.__subclasses__() if you want to handle all"
                " Exceptions"
            )
        else:
            if isinstance(self.E, list):
                validation.validate_each(
                    self.E, Exception
                )
            else:
                validation.validate(self.E, Exception)
        super().__init__(**data)

    def handle(self, request: Request, error: Exception) -> Response:
        raise NotImplementedError()

    class Config:
        arbitrary_types_allowed = True
