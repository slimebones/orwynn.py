from staze.core.error.error import Error
from staze.core.validation import validate


class ParsingError(Error):
    pass


class IntParsingError(ParsingError):
    def __init__(
            self,
            parsed_str: str,
            message: str | None = None,
            status_code: int | None = None) -> None:
        super().__init__(message, status_code)

        validate(parsed_str, str, 'Parsed str')
        if message is None:
            self.message = f'{parsed_str} is not parseable to int'
        

class KeyParsingError(ParsingError):
    def __init__(
            self,
            parsed_map: dict,
            failed_key: str,
            message: str | None = None,
            status_code: int | None = None) -> None:
        super().__init__(message, status_code)

        validate(parsed_map, dict, 'Parsed map')
        validate(failed_key, str, 'Failed key')

        if message is None:
            self.message = f'{parsed_map} has no key: \'{failed_key}\''
