from enum import Enum
from typing import Awaitable, Callable, ClassVar, Generic

from pydantic.generics import GenericModel
from orwynn.mongo import OkEvt
from pykit.log import log
from pykit.singleton import Singleton
from rxcat import (
    Evt,
    Msg,
    MsgFilter,
    PubAction,
    PubOpts,
    Req,
    ServerBus,
    SubOpts,
    TMsg,
)

from orwynn.cfg import TCfg


class SysArgs(GenericModel, Generic[TCfg]):
    bus: ServerBus
    cfg: TCfg

    class Config:
        arbitrary_types_allowed = True

class Internal__SysErr(Exception):
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
    CommonSubMsgFilters: ClassVar[list[MsgFilter]] = []

    def __init__(
        self,
        args: SysArgs
    ):
        self._bus: ServerBus = args.bus
        self._cfg: TCfg = args.cfg
        self._unsubs: list[Callable[[], Awaitable]] = []
        self._internal_is_initd = False
        self._internal_is_enabled = False

    @property
    def is_initd(self) -> bool:
        return self._internal_is_initd

    @property
    def is_enabled(self) -> bool:
        return self._internal_is_enabled

    async def _pub_ok(self, req: Req, pub_opts: PubOpts = PubOpts()):
        await self._pub(OkEvt(rsid=None).as_res_from_req(req), None, pub_opts)

    async def _sub(
        self,
        msg_type: type[TMsg],
        action: Callable[[TMsg], Awaitable],
        opts: SubOpts = SubOpts(),
    ):
        optsf = opts.model_copy(deep=True)
        optsf.filters = [*self.CommonSubMsgFilters, *optsf.filters]
        self._unsubs.append(await self._bus.sub(msg_type, action, optsf))

    async def _pub(
        self,
        msg: Msg,
        pubaction: PubAction | None = None,
        opts: PubOpts = PubOpts(),
    ):
        await self._bus.pub(msg, pubaction, opts)

    async def _pubr(
        self,
        req: Req,
        opts: PubOpts = PubOpts(),
    ) -> Evt:
        return await self._bus.pubr(req, opts)

    async def _internal_init(self, is_silent: bool = False):
        if self._internal_is_initd:
            if is_silent:
                return
            raise Internal__SysErr
        await self.init()
        self._internal_is_initd = True

    async def _internal_enable(self, is_silent: bool = False):
        if self._internal_is_enabled:
            if is_silent:
                return
            raise Internal__SysErr
        await self.enable()
        self._internal_is_enabled = True

    async def _internal_disable(self, is_silent: bool = False):
        if not self._internal_is_enabled:
            if is_silent:
                return
            raise Internal__SysErr
        await self.disable()
        for unsub in self._unsubs:
            await unsub()
        self._internal_is_enabled = False

    async def init(self):
        """
        This is where all bus-related operations, such as subs should be done.

        Also other async tasks can be setup here.
        """

    async def enable(self):
        """
        You should sub to bus only in enable, since auto-unsub works on
        disable.
        """

    async def disable(self):
        """
        When system is disabled, can happen quite often.

        Here is where all subscriptions to the bus are closed internally,
        so make sure you use bus subs only at enable/disable.
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

