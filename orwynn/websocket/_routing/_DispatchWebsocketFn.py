from typing import Awaitable, Callable

from orwynn.websocket._Websocket import Websocket

from ._GenericWebsocketFn import GenericWebsocketFn

DispatchWebsocketFn = Callable[
    [Websocket, GenericWebsocketFn], Awaitable[None]
]
