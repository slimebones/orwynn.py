from typing import Any, Coroutine, Generic, Iterable, Protocol, runtime_checkable
from pydantic import BaseModel

from orwynn import SysArgs
from orwynn.cfg import TCfg

@runtime_checkable
class PluginFn(Protocol, Generic[TCfg]):
    async def __call__(self, args: SysArgs[TCfg]) -> None: ...

class Plugin(BaseModel, Generic[TCfg]):
    name: str
    init: PluginFn | None = None
    destroy: Coroutine[Any, Any, None] | None = None
