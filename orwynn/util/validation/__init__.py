import re
from enum import EnumMeta
from typing import Any

from pydantic import ValidationError as __PydanticValidationError
from pydantic import validator as __pydantic_validator

from orwynn.util.validation.validation_error import (ReValidationError,
                                                     ValidationError)

from .validation_error import ValidationError


def validate(
        obj: Any, expected_type: type | list[type], is_strict: bool = False
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
    if isinstance(expected_type, type):
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
            raise ValidationError(failed_obj=obj, expected_type=expected_type)
    else:
        raise TypeError(
            "{} should be Type or an instance of list"
            .format(expected_type)
        )


def validate_re(string: str, pattern: str) -> None:
    """Validates given string using re.match.
    
    Raises:
        ReValidationError:
            String does not match given pattern.
    """
    if not re.match(pattern, string):
        raise ReValidationError(failed_obj=string, pattern=pattern)


model_validator = __pydantic_validator
ModelValidationError = __PydanticValidationError