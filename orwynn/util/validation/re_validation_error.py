from typing import Any
from orwynn.base.error._Error import Error


class ReValidationError(Error):
    def __init__(
        self,
        message: str = "",
        failed_obj: Any | None = None,
        pattern: str | None = None
    ) -> None:
        if not message and failed_obj is not None and pattern is not None:
            message = \
                f'{repr(failed_obj)} should implement pattern {pattern}'

        super().__init__(message)
