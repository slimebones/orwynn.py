from enum import Enum
from typing import Generic

from pydantic.generics import GenericModel
from pykit.log import log
from pykit.singleton import Singleton
from rxcat import Bus

from orwynn.cfg import TCfg


class SysArgs(GenericModel, Generic[TCfg]):
    bus: Bus
    cfg: TCfg

    class Config:
        arbitrary_types_allowed = True

class internal_SysErr(Exception):
    pass

class internal_FailedSysCase(Enum):
    Init = "init"
    Enable = "enable"
    Disable = "disable"
    Destroy = "destroy"

class internal_FailedSysErr(Exception):
    def __init__(
        self, sys_type: type["Sys"], case: internal_FailedSysCase, why: str
    ):
        msg = f"failed to {case.value} {sys_type}: {why}"
        super().__init__(msg)

class Sys(Singleton, Generic[TCfg]):
    """
    Heart of the app's logic.

    @abs
    """
    def __init__(
        self,
        args: SysArgs
    ):
        self._bus: Bus = args.bus
        self._cfg: TCfg = args.cfg

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

    @classmethod
    async def _internal_destroy(cls):
        try:
            ie = cls.ie()
        except (AttributeError, TypeError):
            # if system hasn't been initialized, we have nothing to do here
            return
        if ie.is_initd:
            try:
                await ie.destroy()
            except Exception as err:
                newerr = internal_FailedSysErr(
                    cls,
                    internal_FailedSysCase.Destroy,
                    f"unhandled err => {err}"
                )
                log.err_or_catch(newerr, 2)
            cls.try_discard()

    async def destroy(self):
        """
        """

