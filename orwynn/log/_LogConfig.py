from orwynn.base import Config
from orwynn.log._LogHandler import LogHandler


class LogConfig(Config):
    handlers: list[LogHandler] | None = None
