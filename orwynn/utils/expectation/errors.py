from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from orwynn.utils.expectation import Expectation


class ExpectationError(Exception):
    """
    Some expectation rule is failed.
    """
    def __init__(
        self,
        *,
        title: str,
        actual_value: Any,
        expected_value: Any,
    ) -> None:
        message: str = \
            f"{title} expected to have value <{expected_value}>," \
            f" got <{actual_value}> instead"
        super().__init__(message)


class UnsupportedExpectationTypeError(Exception):
    """
    Type is not supported by the expectation.
    """
    def __init__(
        self,
        *,
        UnsupportedType: type,
        expectation: "Expectation",
    ) -> None:
        message: str = \
            f"expectation <{expectation}> does not support" \
            f" type <{UnsupportedType}>"
        super().__init__(message)
