from orwynn.src.config.Config import Config
from orwynn.src.log.LogHandler import LogHandler


class LogConfig(Config):
    handlers: list[LogHandler] | None = None
