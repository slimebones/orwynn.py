from typing import Any
from orwynn.base.error.error import Error


class ValidationError(Error):
    def __init__(
            self,
            message: str = "",
            failed_obj: Any | None = None,
            expected_type: type | list[type] | None = None,
        ) -> None:
        if not message and failed_obj and expected_type:
            if isinstance(expected_type, type):
                message = \
                    f'{repr(failed_obj)} should have type:' \
                    f' {expected_type.__name__}'
            elif type(expected_type) is list:
                message = \
                    f'{repr(failed_obj)} should have one type of the following' \
                    f' list: {[type_.__name__ for type_ in expected_type]}'
            else:
                raise TypeError('Unrecognized type of `expected_type`')

        super().__init__(message)


# ReValidationError inherits base Error, not ValidationError, since some old
# features differ from ValidationError
class ReValidationError(Error):
    def __init__(
            self,
            message: str = "",
            failed_obj: Any | None = None,
            pattern: str | None = None
        ) -> None:
        if not message and failed_obj and pattern:
            message = \
                f'{repr(failed_obj)} should implement pattern {pattern}'

        super().__init__(message)
