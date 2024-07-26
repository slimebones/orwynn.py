import argparse
from asyncio import SubprocessTransport
import functools
import inspect
import typing
from contextlib import suppress
from typing import Any, Callable, ClassVar, Coroutine, Iterable, Literal, Self, TypeVar, runtime_checkable

from pykit.code import Ok
from pykit.res import Res
from pykit.log import log
from pykit.singleton import Singleton
from rxcat import Awaitable, BaseModel, RpcFn, ServerBus, ServerBusCfg, SubFn, valerr

from orwynn import App
from orwynn.cfg import Cfg, CfgPackUtils
from orwynn.plugin import Plugin
from orwynn import env
from typing import Any, Generic, Protocol
from pydantic import BaseModel
from rxcat import Mbody, ServerBus, SubFnRetval, SubOpts

from orwynn.cfg import TCfg
from orwynn.models import Flag

__all__ =[
    "SysArgs",
    "SysFn",
    "sys",
    "rpcsys",
    "Plugin",
    "Flag"
]

class SysArgs(BaseModel, Generic[TCfg]):
    app: App
    bus: ServerBus
    cfg: TCfg

@runtime_checkable
class SysFn(Protocol, Generic[TCfg]):
    async def __call__(
            self, args: SysArgs[TCfg], body: Mbody) -> Any:
        ...

def sys(cfgtype: type[TCfg], sub_opts: SubOpts):
    """
    Systems are functions!
    """
    def wrapper(target: SysFn[TCfg]):
        def inner(*args, **kwargs):
            return target(*args, **kwargs)
        App.sys_init_queue.append((cfgtype, target, sub_opts))
        return inner
    return wrapper

def rpcsys(cfgtype: type[TCfg]):
    """
    Systems are functions!
    """
    def wrapper(target: SysFn[TCfg]):
        def inner(*args, **kwargs):
            return target(*args, **kwargs)
        App.rpcsys_init_queue.append((cfgtype, target))
        return inner
    return wrapper

class AppCfg(Cfg):
    std_verbosity: int = 1
    server_bus_cfg: ServerBusCfg = ServerBusCfg()
    plugins: Iterable[Plugin] = []

class App(Singleton):
    sys_init_queue: list[tuple[type[Cfg], SysFn, SubOpts]]
    rpcsys_init_queue: list[tuple[type[Cfg], SysFn]]

    def __init__(self) -> None:
        self._is_initd = False

    async def init(self, cfg: AppCfg):
        if self._is_initd:
            return

        self._bus = ServerBus.ie()
        self._unsubs: list[Callable[[], Awaitable[Res[None]]]] = []

        self._cfg = cfg
        self._init_mode()
        await self._bus.init(self._cfg.server_bus_cfg)
        await self._init_sys()

        self._is_initd = True

    def _init_mode(self):
        self._mode = env.get_mode()
        log.info(f"chosen mode: {self._mode}", 1)

    async def _gen_type_to_cfg(self) -> dict[type[Cfg], Cfg]:
        cfg_pack = await CfgPackUtils.init_cfg_pack()
        cfgsf = await CfgPackUtils.bake_cfgs(self._mode, cfg_pack)
        type_to_cfg: dict[type[Cfg], Cfg] = {}
        for cfg in cfgsf:
            cfg_type = type(cfg)
            if cfg_type is AppCfg:
                self._cfg = typing.cast(AppCfg, cfg)
                log.std_verbosity = self._cfg.std_verbosity
                log.is_debug = env.is_debug()
                continue
            type_to_cfg[cfg_type] = cfg
        return type_to_cfg

    async def destroy(self, is_hard: bool = False):
        for unsub in self._unsubs:
            (await unsub()).atrack("on app destroy unsub")
        if is_hard:
            self.sys_init_queue.clear()
            self.rpcsys_init_queue.clear()

    async def _init_sys(self):
        type_to_cfg = await self._gen_type_to_cfg()

        for cfgtype, sysfn, sub_opts in self.sys_init_queue:
            await self._reg_sys_signature(sysfn)
            cfg = type_to_cfg[cfgtype]
            args = SysArgs(
                app=self,
                bus=self._bus,
                cfg=cfg)
            subfn = functools.partial(sysfn, args)
            unsub = (await self._bus.sub(subfn, sub_opts)).eject()
            self._unsubs.append(unsub)

        for cfgtype, sysfn in self.rpcsys_init_queue:
            await self._reg_sys_signature(sysfn)
            cfg = type_to_cfg[cfgtype]
            args = SysArgs(
                app=self,
                bus=self._bus,
                cfg=cfg)
            rpcfn = functools.partial(sysfn, args)
            # rpc reg depends on proper function name, which we must fix after
            # applying wrapper
            setattr(
                rpcfn,
                "__name__",
                sysfn.__name__.replace("sys__", "sub__"))  # type: ignore
            self._bus.reg_rpc(rpcfn).eject()

    async def _reg_sys_signature(self, sysfn: SysFn) -> Res[None]:
        signature = inspect.signature(sysfn)
        params = list(signature.parameters.values())
        if len(params) != 2:
            return valerr(f"sysfn {sysfn} must accept only two args => skip")
        if params[0].annotation is not SysArgs:
            return valerr(
                f"sysfn {sysfn} accept incorrect \"args\" type"
                f" {params[0].annotation} => skip")
        bodytype = params[1].annotation
        (await self._bus.reg_types([bodytype])).eject()
        return Ok(None)
