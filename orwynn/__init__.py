import functools
import inspect
import typing
from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    Protocol,
    Self,
    runtime_checkable,
)

from pydantic import BaseModel
from pykit.code import Ok
from pykit.log import log
from pykit.res import Res
from pykit.singleton import Singleton
from rxcat import (
    Awaitable,
    Mbody,
    ServerBus,
    ServerBusCfg,
    SubOpts,
    valerr,
)

from orwynn import env
from orwynn._cfg import Cfg, CfgPack, CfgPackUtils, TCfg
from orwynn._models import Dto, Fdto, Flag, TDto, TFdto, TUdto, Udto
from orwynn._plugin import Plugin

__all__ =[
    "App",
    "AppCfg",
    "Cfg",
    "CfgPack",
    "SysArgs",
    "SysFn",
    "sys",
    "rpcsys",
    "Plugin",
    "Flag",
    "Dto",
    "Udto",
    "Fdto",
    "TDto",
    "TUdto",
    "TFdto"
]

class SysArgs(BaseModel, Generic[TCfg]):
    app: "App"
    bus: ServerBus
    cfg: TCfg

    class Config:
        arbitrary_types_allowed = True

@runtime_checkable
class SysFn(Protocol, Generic[TCfg]):
    async def __call__(
            self, args: SysArgs[TCfg], body: Mbody) -> Any:
        ...

def sys(cfgtype: type[TCfg], sub_opts: SubOpts = SubOpts()):
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
    extend_cfg_pack: CfgPack = {}

class App(Singleton):
    sys_init_queue: list[tuple[type[Cfg], SysFn, SubOpts]] = []
    rpcsys_init_queue: list[tuple[type[Cfg], SysFn]] = []
    _SYS_SIGNATURE_PARAMS_LEN: int = 2

    def __init__(self) -> None:
        self._is_initd = False

    async def init(self, cfg: AppCfg = AppCfg()) -> Self:
        if self._is_initd:
            return self

        self._bus = ServerBus.ie()
        self._unsubs: list[Callable[[], Awaitable[Res[None]]]] = []

        self._cfg = cfg
        self._init_mode()
        await self._bus.init(self._cfg.server_bus_cfg)

        self._type_to_cfg = await self._gen_type_to_cfg()
        self._plugins = list(self._cfg.plugins)
        await self._init_plugins()
        await self._init_sys()

        self._is_initd = True

        return self

    async def destroy(self, *, is_hard: bool = False):
        if not self._is_initd:
            return
        self._is_initd = False

        # destroy plugins
        for plugin in self._plugins:
            if plugin.cfgtype not in self._type_to_cfg:
                # try to init cfgtype without params
                try:
                    self._type_to_cfg[plugin.cfgtype] = plugin.cfgtype()
                except Exception as err:
                    log.err(
                        f"({plugin}) unspecified config {plugin.cfgtype}"
                        " => skip")
                    continue
            cfg = self._type_to_cfg[plugin.cfgtype]
            args = SysArgs(app=self, bus=self._bus, cfg=cfg)
            if plugin.destroy is not None:
                try:
                    await (await plugin.destroy(args)).atrack(
                        f"({plugin}) destroy")
                except Exception as err:
                    await log.atrack(err, f"({plugin}) destroy")

        # unsub all
        for unsub in self._unsubs:
            (await unsub()).atrack("on app destroy unsub")

        # destroy meta data if needed
        if is_hard:
            self.sys_init_queue.clear()
            self.rpcsys_init_queue.clear()

        # destroy bus data since it's deeply associated with the app
        await self._bus.destroy()

    async def _init_plugins(self):
        for plugin in self._plugins:
            if plugin.cfgtype not in self._type_to_cfg:
                log.err(f"({plugin}) unrecognized cfg type")
                continue
            cfg = self._type_to_cfg[plugin.cfgtype]
            args = SysArgs(app=self, bus=self._bus, cfg=cfg)
            if plugin.init is not None:
                try:
                    await (await plugin.init(args)).atrack(f"({plugin}) init")
                except Exception as err:
                    await log.atrack(err, f"({plugin}) init")

    def _init_mode(self):
        self._mode = env.get_mode()
        log.info(f"chosen mode: {self._mode}", 1)

    async def _gen_type_to_cfg(self) -> dict[type[Cfg], Cfg]:
        cfg_pack = await CfgPackUtils.init_cfg_pack()
        cfg_pack.update(self._cfg.extend_cfg_pack)
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

    async def _init_sys(self):
        for cfgtype, sysfn, sub_opts in self.sys_init_queue:
            if not sysfn.__name__.startswith("sys__"):  # type: ignore
                log.err(
                    f"sysfn {sysfn} name must start with \"sys__\" => skip")
                continue
            await self._reg_sys_signature(sysfn)
            cfg = self._type_to_cfg[cfgtype]
            args = SysArgs(
                app=self,
                bus=self._bus,
                cfg=cfg)
            subfn = functools.partial(sysfn, args)
            subfn.__name__ = sysfn.__name__.replace("sys__", "sub__")  # type: ignore
            unsub = (await self._bus.sub(subfn, sub_opts)).eject()
            self._unsubs.append(unsub)

        for cfgtype, sysfn in self.rpcsys_init_queue:
            if not sysfn.__name__.startswith("sys__"):  # type: ignore
                log.err(
                    f"sysfn {sysfn} name must start with \"sys__\" => skip")
                continue
            await self._reg_sys_signature(sysfn)
            cfg = self._type_to_cfg[cfgtype]
            args = SysArgs(
                app=self,
                bus=self._bus,
                cfg=cfg)
            rpcfn = functools.partial(sysfn, args)
            rpcfn.__name__ = sysfn.__name__.replace("sys__", "sub__")  # type: ignore
            self._bus.reg_rpc(rpcfn).eject()

    async def _reg_sys_signature(self, sysfn: SysFn) -> Res[None]:
        signature = inspect.signature(sysfn)
        params = list(signature.parameters.values())
        if len(params) != self._SYS_SIGNATURE_PARAMS_LEN:
            return valerr(f"sysfn {sysfn} must accept only two args => skip")
        if params[0].annotation is not SysArgs:
            return valerr(
                f"sysfn {sysfn} accept incorrect \"args\" type"
                f" {params[0].annotation} => skip")
        bodytype = params[1].annotation
        (await self._bus.reg_types([bodytype])).eject()
        return Ok(None)
