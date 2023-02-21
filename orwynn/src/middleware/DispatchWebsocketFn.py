from typing import Awaitable, Callable

from orwynn.src.middleware.GenericWebsocketFn import GenericWebsocketFn
from orwynn.src.web.websocket.Websocket import Websocket

DispatchWebsocketFn = Callable[
    [Websocket, GenericWebsocketFn], Awaitable[None]
]
