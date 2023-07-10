"""
Collection of validation functions.
"""
import re
import typing
from inspect import isclass
from pathlib import Path
from typing import Any, Callable, Optional, Sized, TypeVar

from pydantic import ValidationError as _PydanticValidationError
from pydantic import validator as _pydantic_validator
from orwynn.utils.types import AnyCoro

from orwynn.utils.validation.validator import Validator
from orwynn.utils.validation.errors import (ExpectationError,
                                            ReValidationError,
                                            UnknownValidatorError,
                                            ValidationError)

# WARNING: typing aliases are not currently supported so passing types like
#   "dict[str, Any]" to check will produce ValidationError in any case since
#   direct runtime comparison is made.
ValidationExpectedType = type | list[type] | Validator | Path
ApplyExpectedType = TypeVar("ApplyExpectedType")
model_validator = _pydantic_validator
ModelValidationError = _PydanticValidationError


def validate(
    obj: Any,
    expected_type: ValidationExpectedType,
    *,
    is_strict: bool = False
) -> None:
    """Validates given object against expected type.

    Args:
        obj:
            Object to be validated.
        expected_type:
            Type to compare object to.
        is_strict (optional):
            Whether strict check should be performed. If True, direct type
            comparison is made, disallowing subclasses. If False, isinstance()
            comparison is made.
    Raises:
        ValidationError:
            Object did not pass validation.
    """
    if isinstance(expected_type, Validator):
        __check_validator(obj, expected_type)
    elif expected_type is Callable:
        __check_callable(obj, typing.cast(Callable, expected_type), is_strict)
    elif isinstance(expected_type, type):
        __check_type(obj, expected_type, is_strict)
    elif type(expected_type) is list:
        is_matched_type_found: bool = False

        for type_ in expected_type:
            try:
                validate(obj, type_, is_strict=is_strict)
            except ValidationError:
                continue
            else:
                is_matched_type_found = True

        if not is_matched_type_found:
            raise ValidationError(
                failed_obj=obj, expected_type=expected_type
            )
    else:
        raise ValidationError(
            f"{expected_type} should be Type, an instance of list or"
            " Validator"
        )


def validate_each(
    obj: list | tuple | set | frozenset,
    expected_type: ValidationExpectedType,
    *,
    is_strict: bool = False,
    expected_sequence_type: type | None = None,
    should_check_if_empty: bool = False
) -> None:
    """Validates each object in given array against expected type.

    Args:
        obj:
            Object to be validated. Note that not all iterables are accepted,
            only meaningful ones. E.g. there is not sence for this function
            to accept string and validate each char in it.
        expected_type:
            Type to compare object to.
        is_strict (optional):
            Whether strict check should be performed. If True, direct type
            comparison is made, disallowing subclasses. If False, isinstance()
            comparison is made.
        expected_sequence_type (optional):
            To perform checking for the given sequence itself.
        should_check_if_empty (optional):
            Perform checking if given obj is empty.
    """
    validate(obj, [list, tuple, set, frozenset], is_strict=True)

    if expected_sequence_type is not None:
        if expected_sequence_type not in [list, tuple, set, frozenset]:
            raise ValidationError(
                f"expected object type {expected_sequence_type} is neither"
                " list, tuple, set or frozen set"
            )
        validate(obj, expected_sequence_type)

    is_empty: bool = True
    for o in obj:
        is_empty = False
        validate(o, expected_type, is_strict=is_strict)

    if should_check_if_empty and is_empty:
        raise ValidationError("validated iterable shouldn't be empty")


def validate_dict(
    obj: dict,
    expected_types: tuple[ValidationExpectedType, ValidationExpectedType],
    *,
    strict_flags: tuple[bool, bool] | None = None
) -> None:
    """Validates each key and each value in given dict.

    Args:
        obj:
            Dict to be validated.
        expected_types:
            Tuple of expected types for key and expected types for value.
        strict_flags (optional):
            Tuple of flags for strict validation separately for key and for
            value. Defaults to (False, False) which means no strict validation
            neither for key nor for value.

    Raises:
        NothingToValidateError:
            Empty dict given.
        ValidationError:
            Some key or value did not passed the validation.
    """
    if strict_flags is None:
        strict_flags = (False, False)

    validate(obj, dict)
    validate_length(strict_flags, 2)
    validate_each(strict_flags, bool)

    for k, v in obj.items():
        validate(k, expected_types[0], is_strict=strict_flags[0])
        validate(v, expected_types[1], is_strict=strict_flags[1])


def validate_re(string: str, pattern: str) -> None:
    """Validates given string using re.match.

    Args:
        string:
            String to validate.
        pattern:
            Regex pattern to apply.

    Raises:
        ReValidationError:
            String does not match given pattern.
    """
    if not re.match(pattern, string):
        raise ReValidationError(failed_obj=string, pattern=pattern)


def validate_length(obj: Sized, expected_length: int) -> None:
    """Validates length of the given object.

    Args:
        obj:
            Sized object to be validated.
        expected_length:
            Which length is expected.

    Raise:
        ValidationError:
            Given object is not Sized.
        ValidationError:
            Length expectations failed.
    """
    if not hasattr(obj, "__len__"):
        raise ValidationError(
            f"object {obj} should implement \"__len__\" method"
        )

    obj_len: int = len(obj)
    if not obj_len == expected_length:
        raise ValidationError(
            f"sized object {obj} length {obj_len} != "
            f" expected length {expected_length}"
        )


def validate_route(route: str) -> None:
    """Validates route.

    Args:
        route:
            Route to validate.

    Raises:
        ReValidationError:
            Route does not match route pattern.
    """
    validate_re(route, r"^\/(.+\/?)?$")


def apply(
    obj: Any, expected_type: type[ApplyExpectedType]
) -> ApplyExpectedType:
    """Validates given object against given expected type.

    Args:
        obj:
            Object to be validated.
        expected_type:
            Type to check.

    Returns:
        The same object but with given type reference.

    Raises:
        ValidationError:
            Object type is not expected type.
    """
    validate(obj, expected_type)
    return obj


def expect(
    fn: Callable,
    ErrorToExpect: type[Exception],
    *args,
    **kwargs
) -> None:
    """
    Expects given function to raise given error if function is called with
    given args and kwargs.

    Args:
        fn:
            Function to call.
        ErrorToExpect:
            Exception class to expect.
        args:
            Positional arguments to pass to function call.
        kwargs:
            Keyword arguments to pass to function call.

    Raises:
        ExpectationError:
            Given error has not been raised on function's call.
    """
    try:
        fn(*args, **kwargs)
    except ErrorToExpect:
        pass
    else:
        raise ExpectationError(
            f"error {ErrorToExpect} expected on call of function {fn}"
        )


async def expect_async(
    coro: AnyCoro,
    ErrorToExpect: type[Exception]
) -> None:
    """
    Works same as validation.expect, but with async coroutine being tested.
    """
    try:
        await coro
    except ErrorToExpect:
        pass
    else:
        raise ExpectationError(
            f"error {ErrorToExpect} expected on call of coro {coro}"
        )


CheckedObj = TypeVar("CheckedObj")
def check(obj: Optional[CheckedObj]) -> CheckedObj:
    """Checks if given object is not None.

    Raises:
        ValidationError:
            If given object is None.
    """
    if obj is None:
        raise ValidationError(f"shouldn't be None")
    return obj


def __check_validator(obj: Any, validator: Validator) -> None:
    match validator:
        case Validator.SKIP:
            return
        case _:
            raise UnknownValidatorError(
                f"unknown validator {validator}"
            )


def __check_callable(obj: Any, c: Callable, is_strict: bool) -> None:
    if is_strict:
        raise ValueError(
            "expected type is Callable and strict flag is true"
            " which is not logical"
        )
    elif not callable(obj):
        raise ValidationError(
            f"{obj} is not Callable"
        )


def __check_type(obj: Any, t: type, is_strict: bool) -> None:
    if is_strict and type(obj) is t:
        return
    elif isinstance(obj, t):
        return
    elif isclass(obj) and issubclass(obj, t):
        return

    raise ValidationError(
        failed_obj=obj, expected_type=t
    )
