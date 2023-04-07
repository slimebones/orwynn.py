from enum import Enum
from typing import Any, get_args
from orwynn.utils import validation


ErrorCode = int | str | Enum
_ErrorCodeTypes: list[type] = list(get_args(ErrorCode))


def get_error_code(err: Exception) -> ErrorCode:
    """
    Returns an error code if it exists.

    Note that error code should be in class-attribute CODE of the given
    exception and be type of int, str or Enum.

    Args:
        err:
            Exception to get the code from.

    Returns:
        Error code.
    """
    try:
        error_code: ErrorCode = err.CODE  # type: ignore
    except AttributeError as _stack_err:
        raise AttributeError(
            f"no specified CODE for error {err}"
        )

    try:
        validation.validate(
            error_code, _ErrorCodeTypes
        )
    except validation.ValidationError as _stack_err:
        raise validation.ValidationError(
            f"error code type should be one of {_ErrorCodeTypes}"
        ) from _stack_err

    return error_code
