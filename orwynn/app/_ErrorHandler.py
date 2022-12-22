from typing import Any, ClassVar, TYPE_CHECKING
from orwynn.base.model.Model import Model
from orwynn.util import validation
from orwynn import app
from orwynn.util.web import Request, Response


class ErrorHandler(Model):
    """Handles outcoming errors from the application.

    Method handle(...) should be redefined in subclass in order to work.
    """
    E: ClassVar[type[Exception] | None] = None
    app: app.AppService

    def __init__(self, **data: Any) -> None:
        if self.E is None:
            raise TypeError(
                f"{self.__class__} error class is not set"
            )
        else:
            validation.validate(self.E, Exception)
        super().__init__(**data)

    def handle(self, request: Request, error: Exception) -> Response:
        raise NotImplementedError()

    class Config:
        arbitrary_types_allowed = True
