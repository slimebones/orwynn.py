import importlib
import typing
from contextlib import suppress
from typing import Callable, Self

import aiohttp.web
from pydantic import ValidationError
from pykit.log import log
from rxcat import Bus

from orwynn.app import App
from orwynn.cfg import Cfg
from orwynn.sys import (
    Sys,
    SysArgs,
    internal_FailedSysCase,
    internal_FailedSysErr,
    internal_SysErr,
)
from orwynn.ws import Ws


class BootCfg(Cfg):
    verbosity: int = 0
    routedef_funcs: list[Callable[[], aiohttp.web.RouteDef]] | None = None

class Boot(Sys[BootCfg]):
    @classmethod
    async def init_boot(cls) -> Self:
        bus = Bus.ie()
        await bus.init()

        # attach empty boot cfg now, later the boot will adjust it for itself
        boot = cls(SysArgs(bus=bus, cfg=BootCfg()))

        # no err guards here: if we fail - we fail
        await boot._internal_init(is_silent=True)  # noqa: SLF001
        await boot._internal_enable(is_silent=True)  # noqa: SLF001

        return boot

    @classmethod
    async def get_app(cls) -> aiohttp.web.Application:
        boot = await cls.init_boot()

        app = App()
        routedefs = []
        routedef_funcs = boot._cfg.routedef_funcs  # noqa: SLF001
        if routedef_funcs:
            routedefs = [func() for func in routedef_funcs]
        app.add_routes([
            aiohttp.web.get("/rx", boot._handle_ws),  # noqa: SLF001
            *routedefs
        ])

        return app

    @classmethod
    async def run(cls):  # add server args here
        """
        Runs the app using a server.
        """
        app = await cls.get_app()
        aiohttp.web.run_app(app)

    async def init(self):
        cfg_pack = await self._init_cfg_pack()
        type_to_cfg: dict[type[Cfg], Cfg] = {}
        for cfg in cfg_pack:
            cfg_type = type(cfg)
            if cfg_type is BootCfg:
                self._cfg = typing.cast(BootCfg, cfg)
                log.verbosity = self._cfg.verbosity
                continue
            type_to_cfg[cfg_type] = cfg

        await self._init_sys(type_to_cfg)
        # for now all systems are enabled without an option to change, later
        # we will do something more flexible
        await self._enable_all_sys()

    async def _handle_ws(self, webreq: aiohttp.web.BaseRequest):
        ws = Ws()
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
                        raise TypeError  # noqa: TRY301
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

            sys_cfg_type = Cfg

            # for systems without generic definitions (just Sys instead of
            # Sys[MyCfg]) orig bases would be singleton and typing.Generic,
            # so in this case we sure sys does not want to use cfg
            with suppress(IndexError):
                sys_cfg_type = typing.get_args(
                    sys_type.__orig_bases__[0]  # type: ignore
                )[0]

            if not issubclass(sys_cfg_type, Cfg):
                log.err(f"wrong {sys_type} cfg generic: {sys_cfg_type}")
                sys_cfg_type = None

            if sys_cfg_type is not None:
                if sys_cfg_type in type_to_cfg:
                    sys_cfg = type_to_cfg[sys_cfg_type]
                    assert isinstance(sys_cfg, sys_cfg_type)
                else:
                    # try start defined cfg without arguments - if fail, the
                    # system init must fail
                    try:
                        sys_cfg = sys_cfg_type()  # type: ignore
                    except ValidationError:
                        newerr = internal_FailedSysErr(
                            sys_type,
                            internal_FailedSysCase.Init,
                            f" define {sys_cfg_type}"
                        )
                        log.err_or_catch(newerr, 2)
                        continue

            try:
                await sys_type(SysArgs(  # noqa: SLF001
                    bus=self._bus,
                    cfg=sys_cfg
                ))._internal_init()
            except internal_SysErr as err:
                log.catch(err)
            except Exception as err:
                newerr = internal_FailedSysErr(
                    sys_type,
                    internal_FailedSysCase.Init,
                    f"unhandled err => {err}"
                )
                log.err_or_catch(newerr, 2)

    async def _enable_all_sys(self):
        for sys_type in Sys.__subclasses__():
            try:
                await sys_type.ie().enable()
            except internal_SysErr as err:  # noqa: PERF203
                log.catch(err)
            except Exception as err:
                newerr = internal_FailedSysErr(
                    sys_type,
                    internal_FailedSysCase.Enable,
                    f"unhandled err => {err}"
                )
                log.err_or_catch(newerr, 2)

