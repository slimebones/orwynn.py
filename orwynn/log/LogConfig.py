from orwynn.config.Config import Config
from orwynn.log.LogHandler import LogHandler


class LogConfig(Config):
    handlers: list[LogHandler] | None = None
