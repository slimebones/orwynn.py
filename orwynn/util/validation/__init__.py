"""Collection of validation functions.

In future the framework might introduce special flags (or read Python's
optimization flag -O) to not execute such functions.
"""
import re
from typing import Any, Sized

from pydantic import ValidationError as __PydanticValidationError
from pydantic import validator as __pydantic_validator

from orwynn.util.validation.nothing_to_validate_error import NothingToValidateError
from orwynn.util.validation.re_validation_error import ReValidationError
from orwynn.util.validation.unknown_validator_error import UnknownValidatorError
from orwynn.util.validation.validation_error import ValidationError
from orwynn.util.validation.validator import Validator


__ExpectedType = type | list[type] | Validator


def validate(
    obj: Any, expected_type: __ExpectedType, *, is_strict: bool = False
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
        match expected_type:
            case Validator.SKIP:
                return
            case _:
                raise UnknownValidatorError(
                    f"unknown validator {expected_type}"
                )
    elif isinstance(expected_type, type):
        if is_strict:
            if (
                type(obj) is not expected_type
                and not issubclass(obj, expected_type)
            ):
                raise ValidationError(
                    failed_obj=obj, expected_type=expected_type
                )
        else:
            if (
                not isinstance(obj, expected_type)
                and not issubclass(obj, expected_type)
            ):
                raise ValidationError(
                    failed_obj=obj, expected_type=expected_type
                )
    elif type(expected_type) is list:
        is_matched_type_found: bool = False

        for type_ in expected_type:
            if type(obj) is type_:
                is_matched_type_found = True

        if not is_matched_type_found:
            raise ValidationError(
                failed_obj=obj, expected_type=expected_type
            )
    else:
        raise TypeError(
            f"{expected_type} should be Type, an instance of list or"
            " Validator"
        )


def validate_each(
    obj: list | tuple | set | frozenset,
    expected_type: __ExpectedType,
    *,
    is_strict: bool = False,
    expected_obj_type: type | None = None,
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
        expected_obj_type (optional):
            To perform checking for the given object itself.
        should_check_if_empty (optional):
            Perform checking if given obj is empty.
    """
    validate(obj, [list, tuple, set, frozenset])

    if expected_obj_type is not None:
        if expected_obj_type not in [list, tuple, set, frozenset]:
            raise ValidationError(
                f"expected object type {expected_obj_type} is neither"
                " list, tuple, set or frozen set"
            )
        validate(obj, expected_obj_type)

    is_empty: bool = True
    for o in obj:
        is_empty = False
        validate(o, expected_type, is_strict=is_strict)

    if should_check_if_empty and is_empty:
        raise ValidationError("validated iterable shouldn't be empty")


def validate_dict(
    obj: dict,
    expected_types: tuple[__ExpectedType, __ExpectedType],
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
    validate_each(expected_types, [type, list[type]])
    validate_length(strict_flags, 2)
    validate_each(strict_flags, bool)

    if obj == {}:
        raise NothingToValidateError("empty dict given for validation")

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


model_validator = __pydantic_validator
ModelValidationError = __PydanticValidationError
