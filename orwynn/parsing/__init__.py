from types import NoneType
from typing import Any, TypeVar

from orwynn.parsing.parsing_error import (KeyParsingError, ParsingError,
                                          StrIntParsingError)
from orwynn.validation import validate

ParsedEntity = TypeVar('ParsedEntity', bound=Any)


def parse_bool(entity: str | bool) -> bool:
    """Parses given entity to boolean logic.

    If an entity is a simple bool, nothing special happened.
    If an entity is a string, parsing is performed according following rules:
    - "true" => True
    - "false" => False
    - Other cases lead to an ParsingError

    Returns:
        Boolean flag after parsing.

    Raises:
        ParsingError:
            Cannot parse given entity to boolean.
    """
    res: bool

    validate(entity, [bool, str])

    if type(entity) is str:
        match entity:
            case 'true':
                res = True
            case 'false':
                res = False
            case _:
                raise ParsingError(
                    'Str entity to transform to bool should have value'
                    ' `true` or `false`')
    elif type(entity) is bool:
        res = entity
    else:
        raise

    return res


def parse_int(entity: int | str) -> int:
    """Parses given entity to an integer.

    If str accepted, converts it to integer.

    Returns:
        Entity converted to an integer

    Raises:
        StrIntParsingError:
            Cannot parse str to int - in case if entity is a str.
    """
    res: int

    validate(entity, [int, str])

    if type(entity) is int:
        res = entity
    elif type(entity) is str:
        try:
            res = int(entity)
        except ValueError:
            raise StrIntParsingError(failed_str=entity)
    else:
        raise

    return res


def parse_key(
    key: str,
    entity: dict,
    default_value: Any = None,
    post_validation_type: type | list[type] | None = None,
    is_post_validation_strict: bool = False
) -> Any:
    """Parses a value from an entity by given key.

    Apply validation.validate() on result if `post_validation_type` given.

    Args:
        key:
            Key to be parsed.
        entity:
            Entity to be parsed from.
        default_value:
            Default value to be assigned to result if key was not found.
        post_validation_type (optional):
            Type to validate parsed value afterwards.

    Returns:
        Value parsed.

    Raises:
        KeyParsingError:
            If parsing failed and default_value is not set.
    """
    validate(entity, dict)
    validate(key, str)
    validate(
        post_validation_type, [type, list, NoneType], is_strict=False
    )

    try:
        value: Any = entity[key]
    except KeyError:
        if default_value is None:
            raise KeyParsingError(parsed_map=entity, failed_key=key)
        else:
            value = default_value
    else:
        if post_validation_type is not None:
            validate(
                value,
                post_validation_type,
                is_strict=is_post_validation_strict
            )

    return value
