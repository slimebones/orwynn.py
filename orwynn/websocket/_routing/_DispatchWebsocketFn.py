from typing import Awaitable, Callable

from ._GenericWebsocketFn import GenericWebsocketFn
from orwynn.websocket import Websocket

DispatchWebsocketFn = Callable[
    [Websocket, GenericWebsocketFn], Awaitable[None]
]
