from typing import Any, ClassVar, Self

import loguru

from orwynn.app.App import App
from orwynn.base.service.framework_service import FrameworkService
from orwynn.boot.BootMode import BootMode
from orwynn.log.LogConfig import LogConfig
from orwynn.log.LogHandler import LogHandler
from orwynn.proxy.BootProxy import BootProxy


class Log(FrameworkService):
    """Logs messages across the app.
    """
    _logger: ClassVar = loguru.logger

    def __init__(
        self,
        config: LogConfig,
        app: App,
        **kwargs: dict[str, Any]
    ) -> None:
        super().__init__()

        self._config = config
        self._app = app

        self._extra: dict[str, Any] = kwargs

        if config.handlers:
            for handler in config.handlers:
                self._add_handler(handler)

        self.debug = self._logger.bind(**self._extra).debug
        self.info = self._logger.bind(**self._extra).info
        self.warning = self._logger.bind(**self._extra).warning
        self.error = self._logger.bind(**self._extra).error
        self.critical = self._logger.bind(**self._extra).critical
        self.ctx = self._logger.bind(**self._extra).contextualize
        self._catch = self._logger.catch

    @classmethod
    def catch(cls, *args, **kwargs):
        return cls._logger.catch(*args, **kwargs)

    def bind(self, **kwargs) -> Self:
        """Creates a new log service with extra parameters.

        Attributes:
            kwargs:
                Extra parameters to apply.

        Returns:
            New log.
        """
        # No need to validate kwargs keys since Python does it for us if input
        # is like `bind(**{1: "str1", 2: "str2"})` - TypeError is raised
        return self.__class__(self._config, self._app, **kwargs)

    def _add_handler(self, handler: LogHandler) -> None:
        if BootProxy.ie().mode == BootMode.PROD:
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
