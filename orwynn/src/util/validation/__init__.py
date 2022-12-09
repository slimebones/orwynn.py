import re
from enum import EnumMeta
from typing import Any

from orwynn.src.util.validation.validation_error import (ReValidationError,
                                                  ValidationError)


def validate(
        obj: Any, expected_type: type | list[type], is_strict: bool = False
    ) -> None:
    """Validates given object against expected type.

    Args:
        obj:
            Object to be validated
        expected_type:
            Type to compare object to
        is_strict (optional):
            Whether strict check should be performed. If True, direct type
            comparison is made, disallowing subclasses. If False, isinstance()
            comparison is made
    Raises:
        ValidationError:
            Object did not pass validation
    """
    if isinstance(expected_type, type):
        if is_strict:
            if type(obj) is not expected_type:
                raise ValidationError(obj, expected_type)
        else:
            if not isinstance(obj, expected_type):
                raise ValidationError(obj, expected_type)
    elif type(expected_type) is list:
        found: bool = False

        for type_ in expected_type:
            if type(obj) is type_:
                found = True
        
        if not found:
            raise ValidationError(obj, expected_type)
    else:
        raise TypeError('Expected type should be `type` type')


def validate_re(string: str, pattern: str) -> None:
    """Validates given string using re.match.
    
    Raises:
        ReValidationError:
            String does not match given pattern.
    """
    if not re.match(pattern, string):
        raise ReValidationError(string, pattern)