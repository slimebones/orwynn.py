import functools
import inspect
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
from yon import (
    Msg,
    ServerBus,
    ServerBusCfg,
    SubOpts,
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
    "SysFn",
    "Plugin"
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
        self, msg: Msg, args: SysArgs[TCfg]
    ) -> Any:
        ...

@runtime_checkable
class RsysFn(Protocol, Generic[TCfg]):
    async def __call__(
        self, body: Msg, args: SysArgs[TCfg]
    ) -> Res[Any]:
        ...

@runtime_checkable
class PluginFn(Protocol, Generic[TCfg]):
    async def __call__(self, args: "SysArgs[TCfg]") -> Res[None]: ...

class OptedSysFn(Generic[TCfg]):
    fn: SysFn[TCfg]
    opts: SubOpts

class OptedRsysFn(Generic[TCfg]):
    fn: RsysFn[TCfg]
    opts: None

class Plugin(BaseModel, Generic[TCfg]):
    name: str
    cfgtype: type[TCfg]

    global_sys_opts: SubOpts = SubOpts()
    # TODO: impl rpc opts once it gets support at yon
    global_rsys_opts: None = None

    sys: list[SysFn[TCfg] | OptedSysFn[TCfg]] | None = None
    rsys: list[RsysFn[TCfg] | OptedRsysFn[TCfg]] | None = None
    reg_types: list[type | Coded[type]] | None = None

    init: PluginFn[TCfg] | None = None
    destroy: PluginFn[TCfg] | None = None
    postinit: PluginFn[TCfg] | None = None
    """
    Called once all other plugins are initialized.
    """

    def __str__(self) -> str:
        return f"<plugin \"{self.name}\" of cfgtype {self.cfgtype}>"

    def __hash__(self) -> int:
        return hash(id(self))

    class Config:
        arbitrary_types_allowed = True

class AppCfg(Cfg):
    std_verbosity: int = 1
    server_bus_cfg: ServerBusCfg = ServerBusCfg()
    plugins: list[Plugin] = []
    extend_cfg_pack: CfgPack = {}

class App(Singleton):
    _SYS_SIGNATURE_PARAMS_LEN: int = 2

    def __init__(self) -> None:
        self._is_initd = False

    def get_bus(self) -> Res[ServerBus]:
        if not self._is_initd:
            return valerr("not initialized")
        return Ok(self._bus)

    async def init(self, cfg: AppCfg = AppCfg()) -> Self:
        if self._is_initd:
            return self

        self._bus = ServerBus.ie()
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
            global_sys_opts_dump = {}
            if plugin.global_sys_opts:
                global_sys_opts_dump = plugin.global_sys_opts.model_dump()

            for sysfn_or_opted in plugin.sys:
                if isinstance(sysfn_or_opted, OptedSysFn):
                    sub_opts = SubOpts.model_validate({
                        **global_sys_opts_dump,
                        **sysfn_or_opted.opts.model_dump()
                    })
                    # merge known lists instead of overwrite
                    if plugin.global_sys_opts:
                        sub_opts.conditions = [
                            *(plugin.global_sys_opts.conditions or []),
                            *(sub_opts.conditions or [])
                        ]
                        sub_opts.inp_filters = [
                            *(plugin.global_sys_opts.inp_filters or []),
                            *(sub_opts.inp_filters or [])
                        ]
                        sub_opts.out_filters = [
                            *(plugin.global_sys_opts.out_filters or []),
                            *(sub_opts.out_filters or [])
                        ]
                    sysfn = sysfn_or_opted.fn
                else:
                    sub_opts = plugin.global_sys_opts or SubOpts()
                    sysfn = sysfn_or_opted

                destructor = await self._init_sys(
                    sysfn,
                    plugin,
                    sub_opts)
                if destructor:
                    if plugin not in self._plugin_to_destructors:
                        self._plugin_to_destructors[plugin] = []
                    self._plugin_to_destructors[plugin].append(destructor)

    async def _init_plugin_rsystems(self, plugin: Plugin):
        if plugin.rsys:
            # TODO: add rpc opts as soon as it's supported by yon
            for rsysfn_or_opted in plugin.rsys:
                if isinstance(rsysfn_or_opted, OptedRsysFn):
                    rsysfn = rsysfn_or_opted.fn
                else:
                    rsysfn = rsysfn_or_opted

                destructor = await self._init_rsys(
                    rsysfn,
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

    async def _init_sys(
            self,
            sysfn: SysFn[TCfg],
            plugin: Plugin,
            sub_opts: SubOpts) -> Coroutine[Any, Any, Res[None]] | None:
        cfgtype = plugin.cfgtype
        if not sysfn.__name__.startswith("sys__"):  # type: ignore
            log.err(
                f"sysfn {sysfn} name must start with \"sys__\" => skip")
            return None
        await self._reg_sys_signature(sysfn)
        cfg = self._type_to_cfg[cfgtype]
        args = SysArgs(
            app=self,
            bus=self._bus,
            cfg=cfg)
        subfn = functools.partial(sysfn, args)
        subfn.__name__ = sysfn.__name__.replace("sys__", "sub__")  # type: ignore

        unsub_coro_res = typing.cast(
            Res[Coroutine[Any, Any, Res[None]]],
            (await self._bus.sub(subfn, sub_opts)))
        return unsub_coro_res.eject()

    async def _init_rsys(
            self,
            rsysfn: RsysFn[TCfg],
            plugin: Plugin)  -> Coroutine[Any, Any, Res[None]] | None:
        cfgtype = plugin.cfgtype

        if not rsysfn.__name__.startswith("rsys__"):  # type: ignore
            log.err(
                f"rsys {rsysfn} name must start with \"rsys__\" => skip")
            return None

        # no need to reg signature for rpc function - the body of it
        # doesn't have to have the code

        cfg = self._type_to_cfg[cfgtype]
        args = SysArgs(
            app=self,
            bus=self._bus,
            cfg=cfg)
        rpcfn = functools.partial(rsysfn, args)
        rpcfn_key = rsysfn.__name__.replace("rsys__", "")  # type: ignore
        rpcfn.__name__ = rsysfn.__name__.replace("rsys__", "srpc__")  # type: ignore
        self._bus.reg_rpc(rpcfn, plugin.name + "::" + rpcfn_key).eject()
        return functools.partial(self._dereg_rpc, rpcfn_key)()

    async def _dereg_rpc(self, rpcfn_key: str) -> Res[None]:
        # TODO: replace with bus.dereg_rpc coro once yon supports it
        if rpcfn_key in self._bus._rpckey_to_fn:  # noqa: SLF001
            del self._bus._rpckey_to_fn[rpcfn_key]  # noqa: SLF001
        return Ok(None)

    async def _reg_sys_signature(self, sysfn: SysFn) -> Res[None]:
        signature = inspect.signature(sysfn)
        params = list(signature.parameters.values())
        if len(params) != self._SYS_SIGNATURE_PARAMS_LEN:
            return valerr(f"sysfn {sysfn} must accept only two args => skip")
        # don't check direct "is" since it's associated with generic,
        # thought we're not sure this is the case
        if not issubclass(params[0].annotation, SysArgs):
            return valerr(
                f"sysfn {sysfn} accept incorrect \"args\" type"
                f" {params[0].annotation} => skip")
        bodytype = params[1].annotation
        (await self._bus.reg_types([bodytype])).eject()
        return Ok(None)
