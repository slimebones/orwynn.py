import contextlib
from orwynn.utils.klass import Static
import sys
from typing import TYPE_CHECKING, Any
import typing_extensions
from orwynn.log import Log
from orwynn.log.configs import LogConfig
from orwynn.log.handlers import LogHandler
from orwynn.proxy.boot import BootProxy

if TYPE_CHECKING:
    from orwynn.app import AppMode


class LogUtils(Static):
    catchr = Log.catch(reraise=True)
    """
    Shortcut for Log.catch(reraise=True).

    Does not accept additional arguments.
    """

    @staticmethod
    def catch_error(error: Exception):
        """Reraise error and catch it by logger."""
        # TODO(ryzhovalex):
        #   Find way to remove this last function from exception stack to not
        #   be displayed

        # try-except block for correct linting even if error isn't actually
        # passed up the stack
        with contextlib.suppress(Exception), Log.catch(reraise=False):
            raise error

    @staticmethod
    def configure_log(config: LogConfig, *, app_mode_prod: "AppMode") -> None:
        if config.handlers:
            for handler in config.handlers:
                LogUtils._add_handler(handler, app_mode_prod)

    @staticmethod
    def _add_handler(handler: LogHandler, app_mode_prod: "AppMode") -> int:
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
                case "$stdout":
                    sink = sys.stdout
                case "$stderr":
                    sink = sys.stderr
                case _:
                    # For all other string cases consider the sink as a file
                    # path
                    sink = handler.sink
        else:
            # the sink is given directly to the method as a python object,
            # i.e. add it as it is
            sink = handler.sink

        if BootProxy.ie().mode == app_mode_prod:
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

        return Log.add(
            sink,
            **kwargs
        )


@typing_extensions.deprecated("use LogUtils")
def configure_log(config: LogConfig, *, app_mode_prod: "AppMode") -> None:
    LogUtils.configure_log(config, app_mode_prod=app_mode_prod)
