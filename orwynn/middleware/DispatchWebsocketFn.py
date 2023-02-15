from typing import Awaitable, Callable

from orwynn import web
from orwynn.middleware.GenericWebsocketFn import GenericWebsocketFn

DispatchWebsocketFn = Callable[
    [web.Websocket, GenericWebsocketFn], Awaitable[None]
]
