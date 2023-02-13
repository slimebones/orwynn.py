import sys
from types import NoneType
from typing import Any, Optional
import loguru
from orwynn.log.LOG_EXTRA_RESERVED_FIELDS import LOG_EXTRA_RESERVED_FIELDS
from orwynn.log.LogConfig import LogConfig
from orwynn.log.ReservedExtraFieldError import ReservedExtraFieldError
from orwynn import validation
from orwynn.boot.BootMode import BootMode
from orwynn.log.LogHandler import LogHandler
from orwynn.proxy.BootProxy import BootProxy
from orwynn.service.Service import Service
from orwynn.web.context.RequestContextId import RequestContextId
from orwynn.web.context.UndefinedStorageError import UndefinedStorageError


class Log(Service):
    def __init__(
        self,
        config: LogConfig
    ) -> None:
        super().__init__()
        self.__logger = loguru.logger
        self.__configure(config)

    def debug(
        self,
        message: str,
        *,
        extra: Optional[dict] = None
    ) -> None:
        self.__logger.bind(
            **self.__get_builtin_extra_data(),
            **self.__parse_custom_extra_data(extra)
        ).debug(message)

    def info(
        self,
        message: str,
        *,
        extra: Optional[dict] = None
    ) -> None:
        self.__logger.bind(
            **self.__get_builtin_extra_data(),
            **self.__parse_custom_extra_data(extra)
        ).info(message)

    def warning(
        self,
        message: str,
        *,
        extra: Optional[dict] = None
    ) -> None:
        self.__logger.bind(
            **self.__get_builtin_extra_data(),
            **self.__parse_custom_extra_data(extra)
        ).warning(message)

    def error(
        self,
        message: str,
        *,
        extra: Optional[dict] = None
    ) -> None:
        self.__logger.bind(
            **self.__get_builtin_extra_data(),
            **self.__parse_custom_extra_data(extra)
        ).error(message)

    def add_handler(self, handler: LogHandler) -> int:
        """Adds a new handler.

        Args:
            handler:
                Log handler object to be added.

        Returns:
            Added handler number.
        """
        sink: Any
        if isinstance(handler.sink, str):
            # For apprc-based configuration parse some string literals into
            # actual objects.
            match handler.sink:
                case "stdout":
                    sink = sys.stdout
                case "stderr":
                    sink = sys.stderr
                case _:
                    # For all other string cases consider the sink as a file
                    # path
                    sink = handler.sink
        else:
            # the sink is given directly to the method as a python object,
            # i.e. add it as it is
            sink = handler.sink

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

        handler_kwargs: dict = handler.kwargs or {}
        kwargs: dict = dict(
            level=handler.level,
            format=handler.format,
            serialize=handler.serialize,
            **handler_kwargs
        )
        if isinstance(handler.sink, str):
            kwargs["rotation"] = handler.rotation  # type: ignore

        return self.__logger.add(
            sink,
            **kwargs
        )

    def remove_handler(
        self,
        handler_no: Optional[int] = None
    ) -> None:
        """Removes a handler by its number.

        Args:
            handler_no (optional):
                Number of handler to be removed. By default all handlers are
                removed.
        """
        validation.validate(handler_no, [int, NoneType])
        # Handler numbers are equivalent to logger sinks
        self.__logger.remove(handler_no)

    def __get_builtin_extra_data(self) -> dict:
        request_id: Optional[str]

        try:
            request_id = RequestContextId().get()
        except UndefinedStorageError:
            # Log is not made out of request-response cycle
            request_id = None

        return {
            "request_id": request_id
        }

    def __parse_custom_extra_data(self, extra: Optional[dict]) -> dict:
        if extra is None:
            extra = {}
        for reserved_field in LOG_EXTRA_RESERVED_FIELDS:
            validation.validate(reserved_field, str)
            if reserved_field in extra:
                raise ReservedExtraFieldError(
                    f"field {reserved_field} cannot be set in extra dictionary"
                )
        return validation.apply(extra, dict)

    def __configure(self, config: LogConfig) -> None:
        if config.handlers:
            for handler in config.handlers:
                self.add_handler(handler)
