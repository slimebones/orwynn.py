from collections.abc import Awaitable
from typing import Callable

from orwynn import web

# Callable function which returns an awaitable, see:
#   https://stackoverflow.com/a/59177557/14748231
WebsocketNextCall = Callable[[web.Websocket], Awaitable[None]]
