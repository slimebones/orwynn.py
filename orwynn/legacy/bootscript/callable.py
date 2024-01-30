from typing import Any, Callable, Coroutine

BootscriptCallable = Callable[..., None] | Coroutine[Any, Any, None]
