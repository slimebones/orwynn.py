from typing import Generic, Protocol, runtime_checkable

from pydantic import BaseModel
from pykit.res import Res

from orwynn import SysArgs
from orwynn._cfg import TCfg


@runtime_checkable
class PluginFn(Protocol, Generic[TCfg]):
    async def __call__(self, args: SysArgs[TCfg]) -> Res[None]: ...

class Plugin(BaseModel, Generic[TCfg]):
    name: str
    cfgtype: type[TCfg]
    init: PluginFn[TCfg] | None = None
    destroy: PluginFn[TCfg] | None = None

    def __str__(self) -> str:
        return f"< plugin {self.name} of cfgtype {self.cfgtype} >"