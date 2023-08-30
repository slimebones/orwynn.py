import os
from typing import ClassVar

from orwynn.base.error.errors import MalfunctionError
from orwynn.helpers.web import GenericRequest, GenericResponse
from orwynn.log import LogUtils
from orwynn.proxy.boot import BootProxy
from orwynn.utils import validation
from orwynn.utils.scheme import Scheme


class ErrorHandler:
    """
    Handles outcoming errors from the application.
    Method handle(...) should be redefined in subclass in order to work.

    Attributes:
        E:
            Exception or a list of handled Exceptions.
        PROTOCOL:
            Protocol the handler works with.
        IS_ERROR_CATCH_LOGGED:
            Whether the handled errors should be automatically logged by
            Log.catch. Defaults to True.
    """
    E: ClassVar[type[Exception] | None] = None
    PROTOCOL: Scheme = Scheme.HTTP
    IS_ERROR_CATCH_LOGGED: bool = True

    def __init__(self) -> None:
        if self.E is None:
            raise TypeError(
                f"{self.__class__} error class is not set"
            )
        else:
            validation.validate(self.E, Exception)

        validation.validate(self.PROTOCOL, Scheme)

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

    def _fw_handle_wrapper(
        self,
        request: GenericRequest,
        error: Exception
    ) -> GenericResponse:
        """
        Actual handler called on error occuring.

        Inside it should always propagate the control to self.handle.
        """
        if (
            self.IS_ERROR_CATCH_LOGGED
            # check without an AppMode importing due to circular issues
            and BootProxy.ie().mode.value != "test"
            and not os.getenv(
                "ORWYNN_IS_CATCH_LOGGING_ENABLED_IN_TESTS",
                False
            )
        ):
            LogUtils.catch_error(error)
        return self.handle(request, error)

    def handle(
        self,
        request: GenericRequest,
        error: Exception
    ) -> GenericResponse:
        raise NotImplementedError()
