from typing import ClassVar

from orwynn.indication.IndicationType import IndicationType
from orwynn.proxy.APIIndicationOnlyProxy import APIIndicationOnlyProxy


class Error(Exception):
    """Base error class of the app.

    Class-Attributes:
        INDICATION_TYPE (optional):
            Type to be displayed in final response body. Defaults to ERROR.

    Attributes:
        message (optional):
            Message to be attached to the error.
    """
    INDICATION_TYPE: ClassVar[IndicationType | None] = None

    def __init__(self, message: str = "") -> None:
        super().__init__(message)
        self.message = message

    @property
    def api(self) -> dict:
        """Generates API-complying object using project's defined API
        indication.
        """
        return APIIndicationOnlyProxy.ie().api_indication.digest(self)

    def dict(self, *args, **kwargs) -> dict:
        return {
            "message": self.message
        }
