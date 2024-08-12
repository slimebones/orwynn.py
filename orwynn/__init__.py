from copy import deepcopy
from enum import Enum
import functools
import inspect
from re import L
import typing
from typing import (
    Any,
    Coroutine,
    Generic,
    Protocol,
    Self,
    runtime_checkable,
)

from pydantic import BaseModel
from ryz.code import Coded, Ok
from ryz.log import log
from ryz.res import Err, Res, aresultify
from ryz.singleton import Singleton
from yon.server import (
    Msg,
    Bus,
    BusCfg,
    SubFn,
    SubOpts,
    TMsg_contra,
    valerr,
)

from orwynn import env
from orwynn._cfg import Cfg, CfgPack, CfgPackUtils, TCfg

__all__ =[
    "App",
    "AppCfg",
    "Cfg",
    "CfgPack",
    "SysArgs",
    "Sys",
    "Plugin"
]

class SysArgs(BaseModel, Generic[TCfg]):
    app: "App"
    bus: Bus
    cfg: TCfg

    class Config:
        arbitrary_types_allowed = True

class SysOpts(BaseModel):
    pass

@runtime_checkable
class Sys(Protocol, Generic[TCfg]):
    async def __call__(
        self, msg: Msg, args: SysArgs[TCfg]
    ) -> Any:
        ...

@runtime_checkable
class PluginFn(Protocol, Generic[TCfg]):
    async def __call__(self, args: "SysArgs[TCfg]") -> Res[None]: ...

class OptedSys(Generic[TCfg]):
    fn: Sys[TCfg]
    opts: SysOpts = SysOpts()

class GlobalSysOpts(BaseModel):
    all: SysOpts = SysOpts()
    sys: SysOpts = SysOpts()
    rsys: SysOpts = SysOpts()

class Plugin(BaseModel, Generic[TCfg]):
    """
    # SysOpts merge order

    * app_cfg.global_opts.all
    * app_cfg.global_opts.<sys_type>
    * plugin.global_opts.all
    * plugin.global_opts.<sys_type>
    * opted_sys.opts (if [`OptedSys`] is provided)
    """
    name: str
    cfgtype: type[TCfg]

    global_opts: GlobalSysOpts = GlobalSysOpts()

    sys: list[Sys[TCfg] | OptedSys[TCfg]] | None = None
    rsys: list[Sys[TCfg] | OptedSys[TCfg]] | None = None
    reg_types: list[type | Coded[type]] | None = None

    init: PluginFn[TCfg] | None = None
    destroy: PluginFn[TCfg] | None = None
    postinit: PluginFn[TCfg] | None = None
    """
    Called once all other plugins are initialized.
    """

    def __str__(self) -> str:
        return f"plugin \"{self.name}\" of cfgtype {self.cfgtype}"

    def __hash__(self) -> int:
        return hash(id(self))

    class Config:
        arbitrary_types_allowed = True

class AppCfg(Cfg):
    std_verbosity: int = 1
    server_bus_cfg: BusCfg = BusCfg()
    global_opts: GlobalSysOpts = GlobalSysOpts()
    plugins: list[Plugin] = []
    extend_cfg_pack: CfgPack = {}

class SysType(Enum):
    sys = "sys"
    rsys = "rsys"

def _merge(to_dict: dict, from_dict: dict) -> Res[dict]:
    """
    Updates `to_dict` using recursive strategies, merging all nested mergeable
    collections.
    """
    to_dict = deepcopy(to_dict)

    for k_from, v_from in from_dict.items():
        v = v_from
        if k_from in to_dict:
            v_to = to_dict[k_from]
            if type(v_to) is not type(v_from):
                return valerr(
                    f"incompatible types for dict key {k_from} - {type(v_to)}"
                    f" is not {type(v_from)}"
                )
            elif isinstance(v_to, dict):
                r = _merge(v_to, v_from)
                if isinstance(r, Err):
                    return r
                v = r.okval
            elif isinstance(v_to, list):
                v = v_to.extend(v_from)
            elif isinstance(v_to, set):
                v = v_to.update(v_from)
            # all other types are just overwritten
        to_dict[k_from] = v

    return Ok(to_dict)

def _merge_sys_opts(
    app_cfg: AppCfg,
    plugin: Plugin,
    sys: Sys | OptedSys,
    systype: SysType
) -> SysOpts:
    """
    # Merge order

    * app_cfg.global_opts.all
    * app_cfg.global_opts.<sys_type>
    * plugin.global_opts.all
    * plugin.global_opts.<sys_type>
    * opted_sys.opts (if [`OptedSys`] is provided)
    """
    d = app_cfg.global_opts.all.model_dump()
    match systype:
        case SysType.sys:
            d.update(app_cfg.global_opts.sys.model_dump())
        case SysType.rsys:
            d.update(app_cfg.global_opts.rsys.model_dump())
        case _:
            raise SystemError("panic")

    d.update(plugin.global_opts.all.model_dump())
    match systype:
        case SysType.sys:
            d.update(plugin.global_opts.sys.model_dump())
        case SysType.rsys:
            d.update(plugin.global_opts.rsys.model_dump())
        case _:
            raise SystemError("panic")

    if isinstance(sys, OptedSys):
        d.update(sys.opts.model_dump())

    return SysOpts.model_validate(d)

class App(Singleton):
    _SYS_SIGNATURE_PARAMS_LEN: int = 2

    def __init__(self) -> None:
        self._is_initd = False

    def get_bus(self) -> Res[Bus]:
        if not self._is_initd:
            return valerr("not initialized")
        return Ok(self._bus)

    async def init(self, cfg: AppCfg = AppCfg()) -> Self:
        if self._is_initd:
            return self

        self._bus = Bus.ie()
        self._plugin_to_destructors: dict[
            Plugin, list[Coroutine[Any, Any, Res[None]]]] = {}

        self._cfg = cfg
        self._init_mode()
        await self._bus.init(self._cfg.server_bus_cfg)

        self._type_to_cfg = await self._gen_type_to_cfg()
        self._plugins = list(self._cfg.plugins)
        await self._init_all_plugins()

        self._is_initd = True

        return self

    async def destroy(self):
        if not self._is_initd:
            return
        self._is_initd = False

        await self._destroy_all_plugins()

        # destroy bus data since it's deeply associated with the app
        await self._bus.destroy()

    async def _init_plugin_systems(self, plugin: Plugin):
        if plugin.sys:
            for sys_or_opted in plugin.sys:
                sys_opts = _merge_sys_opts(
                    self._cfg,
                    plugin,
                    sys_or_opted,
                    SysType.sys
                )
                if isinstance(sys_or_opted, OptedSys):
                    sys = sys_or_opted.fn
                else:
                    sys = sys_or_opted

                destructor = await self._init_sys(
                    sys,
                    plugin,
                    sys_opts
                )
                if destructor:
                    if plugin not in self._plugin_to_destructors:
                        self._plugin_to_destructors[plugin] = []
                    self._plugin_to_destructors[plugin].append(destructor)

    async def _init_plugin_rsystems(self, plugin: Plugin):
        if plugin.rsys:
            # TODO: add rpc opts as soon as it's supported by yon
            for sysfn_or_opted in plugin.rsys:
                if isinstance(sysfn_or_opted, OptedSys):
                    sysfn = sysfn_or_opted.fn
                else:
                    sysfn = sysfn_or_opted

                destructor = await self._init_rsys(
                    sysfn,
                    plugin)
                if destructor:
                    if plugin not in self._plugin_to_destructors:
                        self._plugin_to_destructors[plugin] = []
                    self._plugin_to_destructors[plugin].append(destructor)

    async def _init_plugin(self, plugin: Plugin):
        if plugin.reg_types:
            await self._bus.reg_types(plugin.reg_types)

        args_res = self._get_sys_args_for_plugin(plugin)
        if isinstance(args_res, Err):
            await args_res.atrack(f"get args for plugin {plugin}")
            return
        args = args_res.okval

        await self._init_plugin_systems(plugin)
        await self._init_plugin_rsystems(plugin)

        if plugin.init is not None:
            await (await aresultify(plugin.init(args))).atrack(
                f"({plugin}) init")

    async def _destroy_plugin(self, plugin: Plugin):
        assert plugin.cfgtype in self._type_to_cfg, \
            "plugin must be initd in order to be destroyed"
        cfg = self._type_to_cfg[plugin.cfgtype]
        args = SysArgs(app=self, bus=self._bus, cfg=cfg)
        if plugin.destroy is not None:
            await (await aresultify(plugin.destroy(args))).atrack(
                f"({plugin}) destroy")
        if plugin in self._plugin_to_destructors:
            for destructor in self._plugin_to_destructors[plugin]:
                await (await aresultify(destructor)).atrack(
                    f"plugin {plugin} destroy")
            del self._plugin_to_destructors[plugin]

    def _get_sys_args_for_plugin(
            self, plugin: Plugin[TCfg]) -> Res[SysArgs[TCfg]]:
        if plugin.cfgtype not in self._type_to_cfg:
            return valerr(f"({plugin}) unrecognized cfg type")
        cfg = typing.cast(TCfg, self._type_to_cfg[plugin.cfgtype])
        return Ok(SysArgs(app=self, bus=self._bus, cfg=cfg))

    async def _init_all_plugins(self):
        for plugin in self._plugins:
            await self._init_plugin(plugin)
        for plugin in self._plugins:
            if not plugin.postinit:
                continue
            args_res = self._get_sys_args_for_plugin(plugin)
            if isinstance(args_res, Err):
                await args_res.atrack(f"get args for plugin {plugin}")
                continue
            await plugin.postinit(args_res.okval)

    async def _destroy_all_plugins(self):
        for plugin in self._plugins:
            await self._destroy_plugin(plugin)

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

    def _get_msg_type_from_sysfn(self, fn: Sys) -> type:
        sig = inspect.signature(fn)
        params = list(sig.parameters.values())
        param = params[0]
        assert inspect.isclass(param.annotation)
        return param.annotation

    async def _init_sys(
        self,
        sysfn: Sys[TCfg],
        plugin: Plugin,
        sys_opts: SysOpts
    ) -> Coroutine[Any, Any, Res[None]] | None:
        cfgtype = plugin.cfgtype
        cfg = self._type_to_cfg[cfgtype]
        args = SysArgs(
            app=self,
            bus=self._bus,
            cfg=cfg
        )

        # TODO: remove once yon::Bus::sub supports auto signature evaluation
        sig = inspect.signature(sysfn)
        msg_param = sig.parameters.get("msg")
        if not msg_param:
            log.err(f"failed to init {sysfn} - must accept msg parameter")
            return
        msgtype = msg_param.annotation

        subfn = functools.partial(sysfn, args=args)
        unsub = typing.cast(
            Res[Coroutine[Any, Any, Res[None]]],
            (await self._bus.sub(msgtype, subfn, sys_opts))
        )
        return unsub.eject()

    async def _init_rsys(
        self,
        sysfn: Sys[TCfg],
        plugin: Plugin
    )  -> Coroutine[Any, Any, Res[None]] | None:
        cfgtype = plugin.cfgtype

        if not sysfn.__name__.startswith("rsys_"):  # type: ignore
            log.err(
                f"rsys {sysfn} name must start with \"rsys_\" => skip")
            return None

        # no need to reg signature for rpc function - the msg of it
        # doesn't have to have the code

        cfg = self._type_to_cfg[cfgtype]
        args = SysArgs(
            app=self,
            bus=self._bus,
            cfg=cfg)
        rpcfn = functools.partial(sysfn, args=args)
        rpcfn_key = sysfn.__name__.replace("rsys_", "")  # type: ignore
        rpcfn.__name__ = sysfn.__name__.replace("rsys_", "srpc__")  # type: ignore
        self._bus.reg_rpc(rpcfn, plugin.name + "::" + rpcfn_key).eject()
        return functools.partial(self._dereg_rpc, rpcfn_key)()

    async def _dereg_rpc(self, rpcfn_key: str) -> Res[None]:
        # TODO: replace with bus.dereg_rpc coro once yon supports it
        if rpcfn_key in self._bus._rpckey_to_fn:  # noqa: SLF001
            del self._bus._rpckey_to_fn[rpcfn_key]  # noqa: SLF001
        return Ok(None)
