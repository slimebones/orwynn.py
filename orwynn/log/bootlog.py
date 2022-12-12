from datetime import datetime
from enum import Enum
from colorama import Fore


class _BootlogLevel(Enum):
    DEBUG = f"{Fore.BLUE}DEBUG{Fore.RESET}"
    INFO = f"{Fore.CYAN}INFO{Fore.RESET}"
    WARNING = f"{Fore.YELLOW}WARNING{Fore.RESET}"
    ERROR = f"{Fore.RED}ERROR{Fore.RESET}"
    CRITICAL = f"{Fore.RED}CRITICAL{Fore.RESET}"


class bootlog:
    """Logs boottime messages."""
    _BRACKET_CTX: str = "Boot"

    def __init__(self) -> None:
        raise NotImplementedError("don't initialize this class")

    @classmethod
    def _log(cls, message: str, level: _BootlogLevel) -> None:
        formatted_bracket_ctx: str = f"[{cls._BRACKET_CTX} / {level.value}]"
        # Figure out local timezone
        # https://stackoverflow.com/a/39079819/14748231
        formatted_datetime: str = datetime.now().astimezone().strftime(
            r'%Y-%m-%d at %H:%M:%S.%f%z'
        )
        print(f"{formatted_datetime} - {formatted_bracket_ctx} {message}")

    @classmethod
    def debug(cls, message: str) -> None:
        """Logs debug message.

        Attributes:
            message:
                Message to be logged.
        """
        cls._log(message, _BootlogLevel.DEBUG)

    @classmethod
    def info(cls, message: str) -> None:
        """Logs informational message.

        Attributes:
            message:
                Message to be logged.
        """
        cls._log(message, _BootlogLevel.INFO)

    @classmethod
    def warning(cls, message: str) -> None:
        """Logs warning message.

        Attributes:
            message:
                Message to be logged.
        """
        cls._log(message, _BootlogLevel.WARNING)

    @classmethod
    def error(cls, message: str) -> None:
        """Logs warning message.

        Attributes:
            message:
                Message to be logged.
        """
        cls._log(message, _BootlogLevel.ERROR)

    @classmethod
    def critical(cls, message: str) -> None:
        """Logs critical message.

        Are you sure you want to use it?

        Attributes:
            message:
                Message to be logged.
        """
        cls._log(message, _BootlogLevel.CRITICAL)
