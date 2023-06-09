from orwynn.base.config import Config
from orwynn.log.handler import LogHandler


class LogConfig(Config):
    handlers: list[LogHandler] | None = None
