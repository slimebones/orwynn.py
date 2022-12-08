from typing import Callable, Any, TypeVar

from werkzeug.datastructures import MultiDict

from staze.core.parsing.parsing_error import (
    IntParsingError, KeyParsingError, ParsingError)
from staze.core.query_parameter_error import QueryParameterError

from staze.core.filter_query_enum import FilterQueryEnum
from staze.core.validation import validate
from staze.core.database.database import Database


ParsedEntity = TypeVar('ParsedEntity', bound=Any)


def parse(entity: Any, expected_type: type[ParsedEntity]) -> ParsedEntity:
    """Return entity if its type matches `expected_type`.
    
    This is only strict type checking. For advanced checking consider other
    functions of this module.
    """
    if type(entity) is expected_type:
        return entity
    else:
        raise ParsingError(f'Entity {entity} should have type {expected_type}')


def parse_bool(entity: str | bool) -> bool:
    res: bool

    validate(entity, [bool, str], 'Entity')
    
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
    """Validate given entity and try to convert it to integer.

    If str accepted, converts it to integer.
    
    Raise:
        IntParsingError:
            Cannot parse entity

    Return:
        Entity converted to integer
    """
    res: int

    validate(entity, [int, str], 'Entity')

    if type(entity) is int:
        res = entity
    elif type(entity) is str:
        try:
            res = int(entity)
        except ValueError:
            raise IntParsingError(entity)
    else:
        raise

    return res


def parse_key(
        key: str, entity: dict,
        post_validation_type: type | list[type] | None = None,
        default: Any = None,
        strict: bool = False) -> Any:
    """Return value parsed from entity by given key.
    
    Apply validation.validate() on result if `post_validation_type` given.
    """
    validate(entity, dict, 'Map to parse')
    validate(key, str, 'Key')

    try:
        value: Any = entity[key]
    except KeyError:
        if default is None:
            raise KeyParsingError(entity, key)
        else:
            value = default
    else: 
        if post_validation_type is not None:
            validate(
                post_validation_type, [type, list], 'Post validation type',
                strict=False)
            validate(
                value, post_validation_type, key.capitalize(), strict=strict)

    return value
