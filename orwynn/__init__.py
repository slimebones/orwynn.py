from collections import namedtuple
import inspect
import typing
from copy import deepcopy
from typing import (
    Any,
    Coroutine,
    Generic,
    Protocol,
    Self,
    TypeVar,
    runtime_checkable,
)

from pydantic import BaseModel
from ryz.core import Coded, Ok
from ryz import log
from ryz.core import Err, Res, aresultify
from ryz.singleton import Singleton
from yon.server import (
    Bus,
    BusCfg,
    Msg,
    SubFn,
    TMsg_contra,
    Err,
)

from orwynn import env
from orwynn._cfg import Cfg, CfgPack, CfgPackUtils, TCfg
from orwynn._pepel import AsyncPipeline, Pipeline

__all__ =[
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

TMsg = TypeVar("TMsg", bound=Msg)
class SysInp(BaseModel, Generic[TMsg, TCfg]):
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

class SysSpec(Generic[TMsg, TCfg]):
    def __init__(
        self, msgtype: type[TMsg], fn: Sys[TMsg, TCfg]
    ):
        self.msgtype = msgtype
        self.fn = fn

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
    bus_cfg: BusCfg = BusCfg()
    plugins: list[Plugin] = []
    extend_cfg_pack: CfgPack = {}
    reg_scope_model_codes: bool = True
    """
    Whether to automatically register all available [`pydantic::BaseModel`]
    subclasses.
    """

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
                return Err(
                    f"incompatible types for dict key {k_from} - {type(v_to)}"
                    f" is not {type(v_from)}"
                )
            elif isinstance(v_to, dict):
                r = _merge(v_to, v_from)
                if isinstance(r, Err):
                    return r
                v = r.ok
            elif isinstance(v_to, list):
                v = v_to.extend(v_from)
            elif isinstance(v_to, set):
                v = v_to.update(v_from)
            elif isinstance(v_to, (Pipeline, AsyncPipeline)):
                v = v_to.merge_right(v_from)
            # all other types are just overwritten
        to_dict[k_from] = v

    return Ok(to_dict)

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
            Plugin, list[Coroutine[Any, Any, None]]
        ] = {}

        self._cfg = cfg
        self._init_mode()
        await self._bus.init(self._cfg.bus_cfg)

        if cfg.reg_scope_model_codes:
            (await reg_scope_model_codes()).unwrap()

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
        if plugin.reg_types:
            await self._bus.reg_regular_codes(*plugin.reg_types)

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
                await (await aresultify(destructor)).atrack(
                    f"{plugin} destroy"
                )
            del self._plugin_to_destructors[plugin]

    def _get_plugin_args(
        self, plugin: Plugin[TCfg]
    ) -> Res[PluginInp[TCfg]]:
        if plugin.cfgtype not in self._type_to_cfg:
            return Err(f"({plugin}) unrecognized cfg type")
        cfg = typing.cast(TCfg, self._type_to_cfg[plugin.cfgtype])
        return Ok(PluginInp(app=self, bus=self._bus, cfg=cfg))

    async def _init_all_plugins(self):
        for plugin in self._plugins:
            await self._init_plugin(plugin)
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
    ) -> Coroutine[Any, Any, None]:
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
            return await sys(inp)
        return inner
