from collections.abc import Awaitable
from typing import Callable

from orwynn.websocket.websocket import Websocket

# Callable function which returns an awaitable, see:
#   https://stackoverflow.com/a/59177557/14748231
WebsocketNextCall = Callable[[Websocket], Awaitable[None]]
