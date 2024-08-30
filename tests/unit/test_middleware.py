import asyncio

from ryz.core import Code, Ok, Res
from ryz.uuid import uuid4

from orwynn import App, AppCfg, Plugin
from orwynn.middleware import Next
from orwynn.sys import SysInp, SysSpec
from orwynn.yon.server import BusCfg, StaticCodeid
from orwynn.yon.server.msg import Msg
from orwynn.yon.server.transport import Transport
from tests.conftest import Mock_1, MockCfg, MockCon


async def test_one_ok():
    flag = False

    async def mw(inp: SysInp, next: Next) -> Res[Msg]:
        assert isinstance(inp.msg, Mock_1)
        assert inp.msg.key == "hello"
        nonlocal flag
        flag = True
        return await next(inp)

    async def sub(inp: SysInp[Mock_1, MockCfg]) -> Res[Msg]:
        return Ok()

    plugin = Plugin(name="test", cfgtype=MockCfg, sys=[SysSpec(Mock_1, sub)])
    cfg = AppCfg(
        bus_cfg=BusCfg(
            transports=[
                Transport(
                    is_server=True,
                    con_type=MockCon
                )
            ],
            reg_regular_codes=[Mock_1]
        ),
        extend_cfg_pack={
            "test": [
                MockCfg(num=1)
            ]
        },
        middlewares=[mw],
        plugins=[plugin]
    )
    app = await App().init(cfg)
    con = MockCon()
    con_task = asyncio.create_task(app.get_bus().unwrap().con(con))
    await con.client_recv()
    await con.client_send({
        "sid": uuid4(),
        "codeid": (await Code.get_regd_codeid_by_type(Mock_1)).unwrap(),
        "msg": {
            "key": "hello"
        }
    })
    r = await con.client_recv()
    assert r["codeid"] == StaticCodeid.Ok
    assert flag
    con_task.cancel()

async def test_two_ok():
    flag = [False, False]

    async def mw1(inp: SysInp, next: Next) -> Res[Msg]:
        assert isinstance(inp.msg, Mock_1)
        assert inp.msg.key == "hello"
        nonlocal flag
        flag[0] = True
        return await next(inp)

    async def mw2(inp: SysInp, next: Next) -> Res[Msg]:
        assert isinstance(inp.msg, Mock_1)
        assert inp.msg.key == "hello"
        nonlocal flag
        flag[1] = True
        return await next(inp)

    async def sub(inp: SysInp[Mock_1, MockCfg]) -> Res[Msg]:
        return Ok()

    plugin = Plugin(name="test", cfgtype=MockCfg, sys=[SysSpec(Mock_1, sub)])
    cfg = AppCfg(
        bus_cfg=BusCfg(
            transports=[
                Transport(
                    is_server=True,
                    con_type=MockCon
                )
            ],
            reg_regular_codes=[Mock_1]
        ),
        extend_cfg_pack={
            "test": [
                MockCfg(num=1)
            ]
        },
        middlewares=[mw1, mw2],
        plugins=[plugin]
    )
    app = await App().init(cfg)
    con = MockCon()
    con_task = asyncio.create_task(app.get_bus().unwrap().con(con))
    await con.client_recv()
    await con.client_send({
        "sid": uuid4(),
        "codeid": (await Code.get_regd_codeid_by_type(Mock_1)).unwrap(),
        "msg": {
            "key": "hello"
        }
    })
    r = await con.client_recv()
    assert r["codeid"] == StaticCodeid.Ok
    assert all(flag)
    con_task.cancel()

