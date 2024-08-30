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
    RpcFn,
    SubFn,
    SubFnRetval,
    TMsg_contra,
    valerr,
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
    "RsysSpec",
    "SysOpts",
    "reg_scope_model_codes"
]

async def reg_scope_model_codes() -> Res[None]:
    """
    Searches for all subclasses of [pydantic::BaseModel] in the scope, and
    registers a code for those who implement [ryz::code::Coded] trait.
    """
    selected = _get_coded_subclasses(BaseModel)
    return await Bus.ie().reg_types(selected)

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

    def ok(self, msg: TMsg | None = None) -> Res["SysInp[TMsg, TCfg]"]:
        """
        Generates Ok() res with new message.

        Used generally at systems to return a message to publish.
        """
        self.msg = msg  # type: ignore
        return Ok(self)

class SysOpts(BaseModel):
    pipeline_before: AsyncPipeline[SysInp] = AsyncPipeline()
    pipeline_after: AsyncPipeline[SysInp] = AsyncPipeline()

    class Config:
        arbitrary_types_allowed = True

@runtime_checkable
class Sys(Protocol, Generic[TMsg, TCfg]):
    async def __call__(
        self,
        inp: SysInp[TMsg, TCfg]
    ) -> Res[SysInp[TMsg, TCfg]]: ...

class PluginInp(BaseModel, Generic[TCfg]):
    app: "App"
    bus: Bus
    cfg: TCfg

    class Config:
        arbitrary_types_allowed = True

@runtime_checkable
class PluginFn(Protocol, Generic[TCfg]):
    async def __call__(self, inp: "PluginInp[TCfg]") -> Res[None]: ...

class GlobalSysOpts(BaseModel):
    all: SysOpts = SysOpts()
    sys: SysOpts = SysOpts()
    rsys: SysOpts = SysOpts()

class SysSpec(BaseModel, Generic[TMsg_contra, TCfg]):
    # we dont use `type[TMsg_contra]` since pydantic cannot resolve it properly
    msgtype: type
    fn: Sys[TMsg_contra, TCfg]
    opts: SysOpts = SysOpts()

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def new(
        cls,
        msgtype: type[TMsg_contra],
        fn: Sys[TMsg_contra, TCfg],
        opts: SysOpts = SysOpts()
    ) -> Self:
        return cls(msgtype=msgtype, fn=fn, opts=opts)

class RsysSpec(BaseModel, Generic[TMsg_contra, TCfg]):
    key: str
    # we dont use `type[TMsg_contra]` since pydantic cannot resolve it properly
    msgtype: type
    fn: Sys[TMsg_contra, TCfg]
    opts: SysOpts = SysOpts()

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def new(
        cls,
        key: str,
        msgtype: type[TMsg_contra],
        fn: Sys[TMsg_contra, TCfg],
        opts: SysOpts = SysOpts()
    ) -> Self:
        return cls(key=key, msgtype=msgtype, fn=fn, opts=opts)

class Plugin(BaseModel, Generic[TCfg]):
    """
    # SysOpts merge order

    * app_cfg.global_opts.all
    * app_cfg.global_opts.<sys_type>
    * plugin.global_opts.all
    * plugin.global_opts.<sys_type>
    * sys_spec.opts
    """
    name: str
    cfgtype: type[TCfg]

    global_opts: GlobalSysOpts = GlobalSysOpts()

    sys: list[SysSpec] | None = None
    rsys: list[RsysSpec] | None = None
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
    global_opts: GlobalSysOpts = GlobalSysOpts()
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
            elif isinstance(v_to, (Pipeline, AsyncPipeline)):
                v = v_to.merge_right(v_from)
            # all other types are just overwritten
        to_dict[k_from] = v

    return Ok(to_dict)

def _merge_sys_opts(
    app_cfg: AppCfg,
    plugin: Plugin,
    spec: SysSpec | RsysSpec
) -> Res[SysOpts]:
    """
    # Merge order

    * app_cfg.global_opts.all
    * app_cfg.global_opts.<sys_type>
    * plugin.global_opts.all
    * plugin.global_opts.<sys_type>
    * sys_spec.opts
    """
    d = app_cfg.global_opts.all.model_dump()
    if isinstance(spec, SysSpec):
        d = _merge(d, app_cfg.global_opts.sys.model_dump())
        if isinstance(d, Err):
            return d
        d = d.okval
    elif isinstance(spec, RsysSpec):
        d = _merge(d, app_cfg.global_opts.rsys.model_dump())
        if isinstance(d, Err):
            return d
        d = d.okval
    else:
        raise SystemError("panic")  # noqa: TRY004

    d = _merge(d, plugin.global_opts.all.model_dump())
    if isinstance(d, Err):
        return d
    d = d.okval
    if isinstance(spec, SysSpec):
        d = _merge(d, plugin.global_opts.sys.model_dump())
        if isinstance(d, Err):
            return d
        d = d.okval
    elif isinstance(spec, RsysSpec):
        d = _merge(d, plugin.global_opts.rsys.model_dump())
        if isinstance(d, Err):
            return d
        d = d.okval
    else:
        raise SystemError("panic")  # noqa: TRY004

    _merge(d, spec.opts.model_dump())

    return Ok(SysOpts.model_validate(d))

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

    async def _init_plugin_rsystems(self, plugin: Plugin):
        if plugin.rsys:
            # TODO: add rpc opts as soon as it's supported by yon
            for spec in plugin.rsys:
                destructor = await self._init_rsys(
                    spec,
                    plugin
                )
                if destructor:
                    if plugin not in self._plugin_to_destructors:
                        self._plugin_to_destructors[plugin] = []
                    self._plugin_to_destructors[plugin].append(destructor)

    async def _init_plugin(self, plugin: Plugin):
        if plugin.reg_types:
            await self._bus.reg_types(plugin.reg_types)

        args_res = self._get_plugin_args(plugin)
        if isinstance(args_res, Err):
            await args_res.atrack(f"get args for {plugin}")
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
            return valerr(f"({plugin}) unrecognized cfg type")
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
        spec: SysSpec[TMsg_contra, TCfg],
        plugin: Plugin
    ) -> Coroutine[Any, Any, Res[None]] | None:
        sys_opts = _merge_sys_opts(
            self._cfg,
            plugin,
            spec
        ).unwrap()

        cfgtype = plugin.cfgtype
        cfg = self._type_to_cfg[cfgtype]
        inp = SysInp(
            msg=None,
            app=self,
            bus=self._bus,
            cfg=cfg,
            extra={}
        )

        pipeline = sys_opts \
            .pipeline_before \
            .copy() \
            .append(spec.fn) \
            .merge_right(sys_opts.pipeline_after)
        unsub = typing.cast(
            Res[Coroutine[Any, Any, Res[None]]],
            # for now we don't pass yon::SubOpts
            (await self._bus.sub(
                spec.msgtype,
                self._wrap_pipeline_as_sub(pipeline, inp)
            ))
        )
        return unsub.unwrap()

    async def _init_rsys(
        self,
        spec: RsysSpec,
        plugin: Plugin
    )  -> Coroutine[Any, Any, Res[None]] | None:
        sys_opts = _merge_sys_opts(
            self._cfg,
            plugin,
            spec
        ).unwrap()

        cfgtype = plugin.cfgtype

        # no need to reg signature for the rpc function - the msg of it
        # doesn't have to have the code

        cfg = self._type_to_cfg[cfgtype]
        args = SysInp(
            msg=None,
            app=self,
            bus=self._bus,
            cfg=cfg,
            extra={}
        )
        pipeline = sys_opts \
            .pipeline_before \
            .copy() \
            .append(spec.fn) \
            .merge_right(sys_opts.pipeline_after)
        self._bus.reg_rpc(
            plugin.name + "::" + spec.key,
            self._wrap_pipeline_as_rpc(pipeline, args),
            spec.msgtype
        ).unwrap()
        return self._new_dereg_rpc(spec.key)

    def _wrap_pipeline_as_sub(
        self,
        pipeline: AsyncPipeline[SysInp],
        inp: SysInp
    ) -> SubFn:
        # we copy inp here so pipes can skip copying. It's highly recommended
        # for pipes to not create side effects with the inp objects since it's
        # allowed to be changed throughout pipeline.
        inp = inp.model_copy()
        async def inner(msg: Msg) -> SubFnRetval:
            inp.msg = msg
            r = await pipeline(inp)
            if isinstance(r, Err):
                return r
            r = r.okval.msg
            return Ok(r)
        return inner

    def _wrap_pipeline_as_rpc(
        self, pipeline: AsyncPipeline[SysInp], inp: SysInp
    ) -> RpcFn:
        # we copy inp here so pipes can skip copying. It's highly recommended
        # for pipes to not create side effects with the inp objects since they
        # are allowed to be changed throughout pipeline.
        inp = inp.model_copy()
        async def inner(msg: Msg) -> Res[Msg]:
            inp.msg = msg
            r = await pipeline(inp)
            if isinstance(r, Err):
                return r
            r = r.okval.msg
            return Ok(r)
        return inner

    def _new_dereg_rpc(self, rpcfn_key: str) -> Coroutine[Any, Any, Res[None]]:
        async def inner() -> Res[None]:
            # TODO: replace with bus.dereg_rpc coro or, better, with reg_rpc
            #       returned callable once yon supports it
            if rpcfn_key in self._bus._rpckey_to_fn:  # noqa: SLF001
                del self._bus._rpckey_to_fn[rpcfn_key]  # noqa: SLF001
            return Ok(None)
        return inner()
