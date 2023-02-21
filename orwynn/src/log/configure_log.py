import sys
from typing import Any
from orwynn.src.boot.BootMode import BootMode
from orwynn.src.log.Log import Log
from orwynn.src.log.LogConfig import LogConfig
from orwynn.src.log.LogHandler import LogHandler
from orwynn.src.proxy.BootProxy import BootProxy


def configure_log(config: LogConfig) -> None:
    if config.handlers:
        for handler in config.handlers:
            __add_handler(handler)

def __add_handler(handler: LogHandler) -> int:
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

    return Log.add(
        sink,
        **kwargs
    )
