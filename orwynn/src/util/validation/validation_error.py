from typing import Any
from orwynn.src.base.http_error.http_error import HttpError


class ValidationError(HttpError):
    def __init__(
            self,
            failed_obj: Any,
            expected_type: type | list[type],
            status_code: int = 400
        ) -> None:
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

        super().__init__(message, status_code)


# ReValidationError inherits base Error, not ValidationError, since some old
# features differ from ValidationError
class ReValidationError(HttpError):
    def __init__(
            self,
            failed_obj: Any,
            pattern: str,
            status_code: int = 400
        ) -> None:
        message = \
            f'{repr(failed_obj)} should implement pattern {pattern}'
        super().__init__(message, status_code)
