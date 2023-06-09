import sys
from typing import TYPE_CHECKING, Any
from orwynn.log.log import Log
from orwynn.log.config import LogConfig
from orwynn.log.handler import LogHandler
from orwynn.proxy.boot import BootProxy

if TYPE_CHECKING:
    from orwynn.app import AppMode


def configure_log(config: LogConfig, *, app_mode_prod: "AppMode") -> None:
    if config.handlers:
        for handler in config.handlers:
            __add_handler(handler, app_mode_prod)

def __add_handler(handler: LogHandler, app_mode_prod: "AppMode") -> int:
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
