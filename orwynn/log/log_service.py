from datetime import time, timedelta
from typing import Any, Callable

import loguru
from orwynn.app.app_mode_enum import AppModeEnum
from orwynn.app.app_service import AppService
from orwynn.base.config.config import Config
from orwynn.base.model.model import Model
from orwynn.base.service.root_service import RootService


class LogHandler(Model):
    # Only mattering for default values fields are added from loguru, others
    # are moved to kwargs dict. Fields set to None by default will be assigned
    # at runtime depending on some conditions
    sink: Any
    level: int | str | None = None
    format: str | Callable = \
        "{time:%Y.%m.%d at %H:%M:%S:%f%z}" \
        + " | {level} | {extra} >> {message}"
    # Callable here used instead of loguru.RotationFunction since it has
    # problems with importing
    rotation: str | int | time | timedelta | Callable = "10 MB"
    serialize: bool | None = None
    kwargs: dict


class LogConfig(Config):
    handlers: list[LogHandler]


class LogService(RootService):
    """Logs messages across the app.
    """
    def __init__(self, config: LogConfig, app: AppService) -> None:
        super().__init__()
        self._logger = loguru.logger
        self._app = app

        self.debug = self._logger.debug
        self.info = self._logger.info
        self.warning = self._logger.warning
        self.error = self._logger.error
        self.critical = self._logger.critical
        self.ctx = self._logger.contextualize
        
        for handler in config.handlers:
            self._add_handler(handler)

    def _add_handler(self, handler: LogHandler) -> None:
        if self._app.mode_enum == AppModeEnum.PROD:
            if handler.level == None:
                handler.level = "INFO"
            if handler.serialize == None:
                handler.serialize = True
        else:
            if handler.level == None:
                handler.level = "DEBUG"
            if handler.serialize == None:
                handler.serialize = False

        self._logger.add(
            handler.sink,
            level=handler.level,
            format=handler.format,
            rotation=handler.rotation,
            serialize=handler.serialize,
            **handler.kwargs
        )
