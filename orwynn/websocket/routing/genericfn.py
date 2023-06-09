from typing import Awaitable, Callable

GenericWebsocketFn = Callable[..., Awaitable[None]]
