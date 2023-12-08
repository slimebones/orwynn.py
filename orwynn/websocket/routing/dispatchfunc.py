from typing import Awaitable, Callable

from orwynn.websocket.websocket import Websocket

from .genericfunc import GenericWebsocketFn

DispatchWebsocketFn = Callable[
    [Websocket, GenericWebsocketFn], Awaitable[None]
]
