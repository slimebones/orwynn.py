from datetime import datetime
from enum import Enum
from colorama import Fore


class _BootlogLevel(Enum):
    DEBUG = f"{Fore.BLUE}DEBUG{Fore.RESET}"
    INFO = f"{Fore.CYAN}INFO{Fore.RESET}"
    WARNING = f"{Fore.YELLOW}WARNING{Fore.RESET}"
    ERROR = f"{Fore.RED}ERROR{Fore.RESET}"
    CRITICAL = f"{Fore.RED}CRITICAL{Fore.RESET}"


class Bootlog:
    """Logs boottime messages."""
    _BRACKET_CTX: str = "Boot"

    def __init__(self) -> None:
        raise NotImplementedError("don't initialize this class")

    @classmethod
    def _log(cls, *args: str, level: _BootlogLevel, separator: str) -> None:
        message: str = separator.join([str(a) for a in args])
        formatted_bracket_ctx: str = f"[{cls._BRACKET_CTX} / {level.value}]"
        # Figure out local timezone
        # https://stackoverflow.com/a/39079819/14748231
        formatted_datetime: str = datetime.now().astimezone().strftime(
            r'%Y-%m-%d at %H:%M:%S.%f%z'
        )
        print(f"{formatted_datetime} - {formatted_bracket_ctx} {message}")

    @classmethod
    def debug(cls, *args, separator: str = " ") -> None:
        """Logs debug message.

        Attributes:
            args:
                Messages to be joined and logged.
            separator:
                Separation string to be joined to.
        """
        cls._log(*args, level=_BootlogLevel.DEBUG, separator=separator)

    @classmethod
    def info(cls, *args, separator: str = " ") -> None:
        """Logs informational message.

        Attributes:
            args:
                Messages to be joined and logged.
            separator:
                Separation string to be joined to.
        """
        cls._log(*args, level=_BootlogLevel.INFO, separator=separator)

    @classmethod
    def warning(cls, *args, separator: str = " ") -> None:
        """Logs warning message.

        Attributes:
            args:
                Messages to be joined and logged.
            separator:
                Separation string to be joined to.
        """
        cls._log(*args, level=_BootlogLevel.WARNING, separator=separator)

    @classmethod
    def error(cls, *args, separator: str = " ") -> None:
        """Logs error message.

        Attributes:
            args:
                Messages to be joined and logged.
            separator:
                Separation string to be joined to.
        """
        cls._log(*args, level=_BootlogLevel.ERROR, separator=separator)

    @classmethod
    def critical(cls, *args, separator: str = " ") -> None:
        """Logs critical message.

        Are you sure you want to use it?

        Attributes:
            args:
                Messages to be joined and logged.
            separator:
                Separation string to be joined to.
        """
        cls._log(*args, level=_BootlogLevel.CRITICAL, separator=separator)
