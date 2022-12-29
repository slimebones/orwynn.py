from types import NoneType

from orwynn.error.Error import Error
from orwynn.util.validation import validate


class ParsingError(Error):
    def __init__(self, message: str = "") -> None:
        super().__init__(message)


class StrIntParsingError(ParsingError):
    """Error of parsing str to int."""
    def __init__(
        self,
        message: str = "",
        failed_str: str = ""
    ) -> None:
        validate(failed_str, str)

        if not message and failed_str:
            message = f'{failed_str} is not parseable to int'

        super().__init__(message)


class KeyParsingError(ParsingError):
    """Error of parsing key from some map"""
    def __init__(
        self,
        message: str = "",
        parsed_map: dict | None = None,
        failed_key: str = ""
    ) -> None:
        validate(parsed_map, [dict, NoneType])
        validate(failed_key, str)

        if not message and parsed_map and failed_key:
            message = f'{parsed_map} has no key: \'{failed_key}\''

        super().__init__(message)
