from typing import Any

from fastapi.exceptions import (
    RequestValidationError as FastAPIRequestValidationError,
)

RequestValidationException = FastAPIRequestValidationError


class ExpectationError(Exception):
    pass


class NothingToValidateError(Exception):
    """Typically raised if an empty structure is passed to validation function.
    """


class ReValidationError(Exception):
    def __init__(
        self,
        message: str = "",
        failed_obj: Any | None = None,
        pattern: str | None = None,
        *args
    ) -> None:
        if not message and failed_obj is not None and pattern is not None:
            message = \
                f"{repr(failed_obj)} should implement pattern {pattern}"

        super().__init__(message)


class UnknownValidatorError(Exception):
    pass


class ValidationError(Exception):
    def __init__(
        self,
        message: str = "",
        failed_obj: Any | None = None,
        expected_type: type | list[type] | None = None,
        *args
    ) -> None:
        if (
            not message
            and failed_obj is not None
            # No need to add "expected_type is not None" here since we
            # sometimes compare objects to None
        ):
            if isinstance(expected_type, type):
                message = \
                    f"{repr(failed_obj)} should have type:" \
                    f" {expected_type.__name__}"
            elif type(expected_type) is list:
                message = \
                    f"{repr(failed_obj)}" \
                    " should be any type of" \
                    + f" list: {[type_.__name__ for type_ in expected_type]}"
            else:
                raise TypeError("Unrecognized type of `expected_type`")

        super().__init__(message)
