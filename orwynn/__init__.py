import inspect
import typing
from typing import (
    Callable,
    Generic,
    Protocol,
    Self,
    runtime_checkable,
)

from pydantic import BaseModel
from ryz import log
from ryz.core import Coded, Err, Ok, Res, aresultify, resultify
from ryz.singleton import Singleton

from orwynn import env, middleware
from orwynn.cfg import Cfg, CfgPack, CfgPackUtils, TCfg
from orwynn.middleware import Middleware, Next
from orwynn.sys import Sys, SysInp, SysSpec
from orwynn.yon.server import (
    Bus,
    BusCfg,
    Msg,
    SubFn,
    TMsg_contra,
)

__all__ =[
    "Middleware",
    "Next",
    "App",
    "AppCfg",
    "Cfg",
    "CfgPack",
    "SysInp",
    "Sys",
    "Plugin",
    "PluginInp",
    "SysSpec",
    "reg_scope_model_codes"
]

async def reg_scope_model_codes() -> Res[None]:
    """
    Searches for all subclasses of [pydantic::BaseModel] in the scope, and
    registers a code for those who implement [ryz::code::Coded] trait.
    """
    selected = _get_coded_subclasses(BaseModel)
    return await Bus.ie().reg_regular_codes(*selected)

def _get_coded_subclasses(t: type) -> list[type]:
    selected = []
    for _t in t.__subclasses__():
        if getattr(_t, "code", None) is not None:
            selected.append(_t)
        selected.extend(_get_coded_subclasses(_t))
    return selected

class PluginInp(BaseModel, Generic[TCfg]):
    app: "App"
    bus: Bus
    cfg: TCfg

    class Config:
        arbitrary_types_allowed = True

@runtime_checkable
class PluginFn(Protocol, Generic[TCfg]):
    async def __call__(self, inp: "PluginInp[TCfg]") -> Res[None]: ...

class Plugin(BaseModel, Generic[TCfg]):
    name: str
    cfgtype: type[TCfg]

    sys: list[SysSpec] | None = None
    reg_regular_codes: list[type | Coded[type]] = []
    reg_ecodes: list[str] = []

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
    bus_cfg: BusCfg = BusCfg()
    plugins: list[Plugin] = []
    extend_cfg_pack: CfgPack = {}
    reg_scope_model_codes: bool = True
    """
    Whether to automatically register all available [`pydantic::BaseModel`]
    subclasses.
    """
    middlewares: list[Middleware] = []

class App(Singleton):
    _SYS_SIGNATURE_PARAMS_LEN: int = 2

    def __init__(self) -> None:
        self._is_initd = False

    def get_bus(self) -> Res[Bus]:
        if not self._is_initd:
            return Err("not initialized")
        return Ok(self._bus)

    async def init(self, cfg: AppCfg = AppCfg()) -> Self:
        if self._is_initd:
            return self

        self._bus = Bus.ie()
        self._plugin_to_destructors: dict[
            Plugin, list[Callable]
        ] = {}

        self._cfg = cfg
        self._init_mode()
        await self._bus.init(self._cfg.bus_cfg)

        if cfg.reg_scope_model_codes:
            (await reg_scope_model_codes()).unwrap()

        self._type_to_cfg = await self._gen_type_to_cfg()
        self._plugins = list(self._cfg.plugins)
        await self._init_plugins_on_boot()

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
            for spec in plugin.sys:
                destructor = await self._init_sys(
                    spec,
                    plugin
                )
                if destructor:
                    if plugin not in self._plugin_to_destructors:
                        self._plugin_to_destructors[plugin] = []
                    self._plugin_to_destructors[plugin].append(destructor)

    async def _init_plugin(self, plugin: Plugin):
        args_res = self._get_plugin_args(plugin)
        if isinstance(args_res, Err):
            await args_res.atrack(f"get args for {plugin}")
            return
        args = args_res.ok

        await self._init_plugin_systems(plugin)

        if plugin.init is not None:
            await (await aresultify(plugin.init(args))).atrack(
                f"({plugin}) init")

    async def _destroy_plugin(self, plugin: Plugin):
        assert plugin.cfgtype in self._type_to_cfg, \
            "plugin must be initd in order to be destroyed"
        args = self._get_plugin_args(plugin).unwrap()
        if plugin.destroy is not None:
            await (await aresultify(plugin.destroy(args))).atrack(
                f"({plugin}) destroy")
        if plugin in self._plugin_to_destructors:
            for destructor in self._plugin_to_destructors[plugin]:
                await resultify(destructor).atrack(f"{plugin} destroy")
            del self._plugin_to_destructors[plugin]

    def _get_plugin_args(
        self, plugin: Plugin[TCfg]
    ) -> Res[PluginInp[TCfg]]:
        if plugin.cfgtype not in self._type_to_cfg:
            return Err(f"({plugin}) unrecognized cfg type")
        cfg = typing.cast(TCfg, self._type_to_cfg[plugin.cfgtype])
        return Ok(PluginInp(app=self, bus=self._bus, cfg=cfg))

    async def _init_plugins_on_boot(self):
        regular_codes = []
        ecodes = []
        for plugin in self._plugins:
            regular_codes.extend(plugin.reg_regular_codes)
            ecodes.extend(plugin.reg_ecodes)
            await self._init_plugin(plugin)

        # init all codes for plugins once - even if they are gonna be disabled,
        # this won't be done the second time for the same application boot
        (await Bus().reg_regular_codes(*regular_codes, _set_welcome=False))\
            .unwrap()
        (await Bus().reg_ecodes(*ecodes, _set_welcome=True))\
            .unwrap()

        for plugin in self._plugins:
            if not plugin.postinit:
                continue
            args_res = self._get_plugin_args(plugin)
            if isinstance(args_res, Err):
                await args_res.atrack(f"get args for {plugin}")
                continue
            await plugin.postinit(args_res.ok)

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

        log.std_verbosity = self._cfg.std_verbosity
        log.is_debug = env.is_debug()

        for cfg in cfgsf:
            type_to_cfg[type(cfg)] = cfg

        return type_to_cfg

    def _get_msg_type_from_sysfn(self, fn: Sys) -> type:
        sig = inspect.signature(fn)
        params = list(sig.parameters.values())
        param = params[0]
        assert inspect.isclass(param.annotation)
        return param.annotation

    async def _init_sys(
        self,
        spec: SysSpec[TMsg_contra, TCfg],
        plugin: Plugin
    ) -> Callable:
        cfgtype = plugin.cfgtype
        cfg = self._type_to_cfg[cfgtype]
        inp = SysInp(
            msg=None,
            app=self,
            bus=self._bus,
            cfg=cfg,
            extra={}
        )

        unsub = (await self._bus.sub(
            spec.msgtype,
            self._wrap_sys_as_sub(spec.fn, inp)
        ))
        return unsub.unwrap()

    def _wrap_sys_as_sub(
        self,
        sys: Sys,
        inp: SysInp
    ) -> SubFn:
        # we copy inp here so pipes can skip copying. It's highly recommended
        # for pipes to not create side effects with the inp objects since it's
        # allowed to be changed throughout pipeline.
        inp = inp.model_copy()
        async def inner(msg: Msg) -> Res[Msg]:
            inp.msg = msg
            return await middleware.construct(self._cfg.middlewares, sys)(inp)
        return inner

SysInp.model_rebuild()
