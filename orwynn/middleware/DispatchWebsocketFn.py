from typing import Awaitable, Callable

from orwynn.middleware.GenericWebsocketFn import GenericWebsocketFn
from orwynn.web.websocket.Websocket import Websocket

DispatchWebsocketFn = Callable[
    [Websocket, GenericWebsocketFn], Awaitable[None]
]
