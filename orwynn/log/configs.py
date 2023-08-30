from orwynn.base.config import Config
from orwynn.log.handlers import LogHandler


class LogConfig(Config):
    handlers: list[LogHandler] | None = None
