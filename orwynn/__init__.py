import importlib
from pathlib import Path
import typing

import aiohttp.web
from aiohttp.web import WebSocketResponse as Websocket
from pykit.singleton import Singleton
from pydantic import BaseModel
from rxcat import Bus
from pykit.log import log

class Utils:
    """
    Utils base class to handle common static functionality.
    """
    pass

class Cfg(BaseModel):
    """
    Configurational object used to pass initial arguments to the systems.
    """
    pass

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

class BootCfg(Cfg):
    verbosity: int = 0

class Boot(Sys):
    # sorry, Barbara
    def __init__(self):
        self._bus = Bus()
        self._cfg = BootCfg()

    async def run(self):  # add here server args
        """
        Runs the app using a server.
        """
        app = aiohttp.web.Application()
        app.add_routes([aiohttp.web.get("/rx", self._ws_handler)])
        aiohttp.web.run_app(app)

    async def init(self):
        self._root_dir: Path = Path.cwd()

        _cfg_pack = await self._init_cfg_pack()
        _type_to_cfg: dict[type[Cfg], Cfg] = {}
        for cfg in _cfg_pack:
            cfg_type = type(cfg)
            if cfg_type is BootCfg:
                self._cfg = typing.cast(BootCfg, cfg)
                log.verbosity = self._cfg.verbosity
                continue
            _type_to_cfg[cfg_type] = cfg 

        await self._init_sys(_type_to_cfg)
        # for now all systems are enabled without an option to change, later
        # we will do something more flexible
        await self._enable_all_sys()

    async def _ws_handler(self, webreq: aiohttp.web.BaseRequest):
        ws = Websocket()
        await ws.prepare(webreq)

        await self._bus.conn(ws)  # type: ignore

        return ws

    async def _init_cfg_pack(self) -> set[Cfg]:
        pack = set()

        try:
            cfg_module = importlib.import_module("orwynn_cfg")
        except ModuleNotFoundError:
            log.info("config not found => use default", 2)
        else:
            try:
                pack = cfg_module.default
            except AttributeError:
                log.err(
                    "orwynn_cfg.py is defined, but no 'default' object"
                    " is found there => use default",
                    1
                )

            try:
                pack = set(cfg_module.default)
                for cfg in pack:
                    if not isinstance(cfg, Cfg):
                        raise TypeError
            except TypeError:
                log.err(
                    "orwynn_cfg.py::default is expected to be iterable of Cfg"
                    " instances",
                    1
                )

        return pack

    async def _init_sys(self, type_to_cfg: dict[type[Cfg], Cfg]):
        # all systems visible are initialized. System deeper inheritance is
        # disallowed (here skipped). Systems should init only themselves
        # in their "init" method, to avoid perf hits and unecessary imports.
        # 
        # Accesses to bus and other dependent actions should be done in 
        # enable/disable, since this is a safe point where all systems are
        # initialized.
        for sys_type in Sys.__subclasses__():
            if sys_type is self.__class__:
                continue

            sys_cfg = Cfg()
            if sys_type.CfgType is not None:
                if sys_type.CfgType in type_to_cfg:
                    sys_cfg = type_to_cfg[sys_type.CfgType]
                    assert isinstance(sys_cfg, sys_type.CfgType)

            await sys_type(SysArgs(bus=self._bus, cfg=sys_cfg)).init()

    async def _enable_all_sys(self):
        for sys_type in Sys.__subclasses__():
            await sys_type.ie().enable()

