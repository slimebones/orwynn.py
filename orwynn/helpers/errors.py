from typing import Any


class UnsupportedError(Exception):
    """
    Some value is not recozniged/supported by the system.
    """
    def __init__(
        self,
        *,
        title: str | None = None,
        value: Any
    ) -> None:
        message: str

        pre_title: str = ""
        if title is not None:
            pre_title = f"{title}="

        message = f"unsupported value {pre_title}{value}"

        super().__init__(message)
