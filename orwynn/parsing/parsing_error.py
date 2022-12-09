from orwynn.src.base.http_error.error import Error
from orwynn.src.util.validation import validate


class ParsingError(Error):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class StrIntParsingError(ParsingError):
    """Error of parsing str to int."""
    def __init__(
            self,
            failed_str: str
        ) -> None:
        validate(failed_str, str)

        message = f'{failed_str} is not parseable to int'

        super().__init__(message)
        

class KeyParsingError(ParsingError):
    """Error of parsing key from some map"""
    def __init__(
            self,
            parsed_map: dict,
            failed_key: str
        ) -> None:
        validate(parsed_map, dict)
        validate(failed_key, str)

        message = f'{parsed_map} has no key: \'{failed_key}\''

        super().__init__(message)
