from typing import Any, Callable, Coroutine

BootscriptCallable = Callable[..., None] | Coroutine[None, Any, Any]
