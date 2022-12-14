from datetime import time, timedelta
from typing import Any, Callable, Self

import loguru
from orwynn.base.service.framework_service import FrameworkService
from orwynn.boot.boot_mode import BootMode
from orwynn.app.app_service import AppService
from orwynn.base.config.config import Config
from orwynn.base.model.model import Model


class LogHandler(Model):
    # Only mattering for default values fields are added from loguru, others
    # are moved to kwargs dict. Fields set to None by default will be assigned
    # at runtime depending on some conditions
    sink: Any
    level: int | str | None = None
    format: str | Callable = \
        "{time:%Y.%m.%d at %H:%M:%S.%f%z}" \
        + " | {level} | {extra} >> {message}"
    # Callable here used instead of loguru.RotationFunction since it has
    # problems with importing
    rotation: str | int | time | timedelta | Callable = "10 MB"
    serialize: bool | None = None
    kwargs: dict


class LogConfig(Config):
    handlers: list[LogHandler]


class LogService(FrameworkService):
    """Logs messages across the app.
    """
    def __init__(
        self,
        config: LogConfig,
        app: AppService,
        extra: dict[str, Any] | None = None
    ) -> None:
        super().__init__()
        self._config = config
        self._app = app

        if not extra:
            extra = {}
        self._extra: dict[str, Any] = extra

        for handler in config.handlers:
            self._add_handler(handler)

        self._logger = loguru.logger
        self.debug = self._logger.bind(**self._extra).debug
        self.info = self._logger.bind(**self._extra).info
        self.warning = self._logger.bind(**self._extra).warning
        self.error = self._logger.bind(**self._extra).error
        self.critical = self._logger.bind(**self._extra).critical
        self.ctx = self._logger.bind(**self._extra).contextualize

    def bind(self, **kwargs) -> Self:
        """Creates a new log service with extra parameters.

        Attributes:
            kwargs:
                Extra parameters to apply.
        """
        # No need to validate kwargs keys since Python does it for us if input
        # is like `bind(**{1: "str1", 2: "str2"})` - TypeError is raised
        return self.__class__(self._config, self._app, extra=kwargs)

    def _add_handler(self, handler: LogHandler) -> None:
        if self._app.mode == BootMode.PROD:
            if handler.level is None:
                handler.level = "INFO"
            if handler.serialize is None:
                handler.serialize = True
        else:
            if handler.level is None:
                handler.level = "DEBUG"
            if handler.serialize is None:
                handler.serialize = False

        self._logger.add(
            handler.sink,
            level=handler.level,
            format=handler.format,
            rotation=handler.rotation,
            serialize=handler.serialize,
            **handler.kwargs
        )
