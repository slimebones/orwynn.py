from typing import TYPE_CHECKING, Generic, Protocol, TypeVar, runtime_checkable

from ryz.core import Res
from ryz.model import Model

from orwynn.cfg import TCfg
from orwynn.yon.server import Bus
from orwynn.yon.server.msg import Msg

if TYPE_CHECKING:
    from orwynn import App


TMsg = TypeVar("TMsg", bound=Msg)
class SysInp(Model, Generic[TMsg, TCfg]):
    msg: TMsg
    app: "App"
    bus: Bus
    cfg: TCfg
    extra: dict

    class Config:
        arbitrary_types_allowed = True

@runtime_checkable
class Sys(Protocol, Generic[TMsg, TCfg]):
    async def __call__(
        self,
        inp: SysInp[TMsg, TCfg]
    ) -> Res[Msg]: ...

# for now we haven't managed to enforce correct msgtype and fn accepted type
# match, so linter will be silent on these errors
class SysSpec(Generic[TMsg, TCfg]):
    def __init__(
        self, msgtype: type[TMsg], fn: Sys[TMsg, TCfg]
    ):
        self.msgtype = msgtype
        self.fn = fn
