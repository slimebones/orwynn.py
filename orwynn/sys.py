from enum import Enum
from pydantic import BaseModel
from pykit.singleton import Singleton
from rxcat import Bus

from orwynn.cfg import Cfg

class SysArgs(BaseModel):
    bus: Bus
    cfg: Cfg

    class Config:
        arbitrary_types_allowed = True

class Sys(Singleton):
    """
    Heart of the app's logic.

    @abs
    """
    CfgType: type[Cfg] | None = None

    def __init__(
        self,
        args: SysArgs
    ):
        self._bus: Bus = args.bus
        self._cfg: Cfg = args.cfg

        self._internal_is_initd = False
        self._internal_is_enabled = False

    @property
    def is_initd(self) -> bool:
        return self._internal_is_initd

    @property
    def is_enabled(self) -> bool:
        return self._internal_is_enabled

    async def _internal_init(self, is_silent: bool = False):
        if self._internal_is_initd:
            if is_silent:
                return
            raise internal_SysErr
        await self.init()
        self._internal_is_initd = True

    async def _internal_enable(self, is_silent: bool = False):
        if self._internal_is_enabled:
            if is_silent:
                return
            raise internal_SysErr
        await self.enable()
        self._internal_is_enabled = True

    async def _internal_disable(self, is_silent: bool = False):
        if not self._internal_is_enabled:
            if is_silent:
                return
            raise internal_SysErr
        await self.disable()
        self._internal_is_enabled = False

    async def init(self):
        """
        This is where all bus-related operations, such as subs should be done.

        Also other async tasks can be setup here.
        """

    async def enable(self):
        """
        """

    async def disable(self):
        """
        """

class internal_SysErr(Exception):
    pass

class internal_FailedSysCase(Enum):
    Init = "init"
    Enable = "enable"
    Disable = "disable"

class internal_FailedSysErr(Exception):
    def __init__(self, sys_type: type[Sys], case: internal_FailedSysCase, why: str):
        msg = f"failed to {case.value} {sys_type}: {why}"
        super().__init__(msg)
