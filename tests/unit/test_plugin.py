import asyncio

from ryz.core import Code
from ryz.core import Ok, Res, Err
from ryz.uuid import uuid4
from orwynn.yon.server import BusCfg, RpcRecv, RpcSend, Transport, ok

from orwynn import App, AppCfg, Plugin, PluginInp, RsysSpec, SysInp, SysSpec
from tests.conftest import Mock_1, MockCfg, MockCon


async def test_rsys():
    init_flag = False
    destroy_flag = False
    rpc_flag = False

    async def rsys_test(inp: SysInp[Mock_1, MockCfg]) -> Res[SysInp]:
        assert inp.msg.key == "hello"
        nonlocal rpc_flag
        rpc_flag = True
        return inp.ok()

    async def _init(inp: PluginInp[MockCfg]) -> Res[None]:
        nonlocal init_flag
        init_flag = True
        return Ok()

    async def _destroy(inp: PluginInp[MockCfg]) -> Res[None]:
        nonlocal destroy_flag
        destroy_flag = True
        return Ok()

    plugin = Plugin(
        name="test",
        cfgtype=MockCfg,
        init=_init,
        destroy=_destroy,
        rsys=[RsysSpec.new("test", Mock_1, rsys_test)]
    )
    app = await App().init(AppCfg(
        bus_cfg=BusCfg(
            transports=[
                Transport(is_server=True, con_type=MockCon)
            ]
        ),
        plugins=[plugin],
        extend_cfg_pack={
            "test": [
                MockCfg(num=1)
            ]
        }
    ))
    assert init_flag
    assert not destroy_flag

    con = MockCon()
    con_task = asyncio.create_task(app.get_bus().unwrap().con(con))
    await con.client_recv()
    send_msid = uuid4()
    await con.client_send({
        "sid": send_msid,
        "codeid": (await Code.get_regd_codeid_by_type(RpcSend)).unwrap(),
        "msg": {
            "key": "test::test",
            "data": {
                "key": "hello"
            }
        }
    })
    await asyncio.sleep(0.1)
    assert rpc_flag
    recv = await asyncio.wait_for(con.client_recv(), 1)
    assert "msg" not in recv
    assert recv["lsid"] == send_msid
    assert recv["codeid"] \
        == (await Code.get_regd_codeid_by_type(RpcRecv)).unwrap()

    await app.destroy()
    assert destroy_flag
    con_task.cancel()

async def test_rsys_err():
    init_flag = False
    destroy_flag = False
    rpc_flag = False

    async def rsys_test(inp: SysInp[Mock_1, MockCfg]) -> Res[SysInp]:
        assert inp.msg.key == "hello"
        nonlocal rpc_flag
        rpc_flag = True
        return Err("whoops")

    async def _init(inp: PluginInp[MockCfg]) -> Res[None]:
        nonlocal init_flag
        init_flag = True
        return Ok(None)

    async def _destroy(inp: PluginInp[MockCfg]) -> Res[None]:
        nonlocal destroy_flag
        destroy_flag = True
        return Ok(None)

    plugin = Plugin(
        name="test",
        cfgtype=MockCfg,
        init=_init,
        destroy=_destroy,
        rsys=[RsysSpec.new("test", Mock_1, rsys_test)])
    app = await App().init(AppCfg(
        bus_cfg=BusCfg(
            transports=[
                Transport(is_server=True, con_type=MockCon)
            ]
        ),
        plugins=[plugin],
        extend_cfg_pack={
            "test": [
                MockCfg(num=1)
            ]
        }
    ))
    assert init_flag
    assert not destroy_flag

    con = MockCon()
    con_task = asyncio.create_task(app.get_bus().unwrap().con(con))
    await con.client_recv()
    send_msid = uuid4()
    await con.client_send({
        "sid": send_msid,
        "codeid": (await Code.get_regd_codeid_by_type(RpcSend)).unwrap(),
        "msg": {
            "key": "test::test",
            "data": {
                "key": "hello"
            }
        }
    })
    await asyncio.sleep(0.1)
    assert rpc_flag
    recv = await asyncio.wait_for(con.client_recv(), 1)
    assert recv["lsid"] == send_msid
    assert recv["codeid"] \
        == (await Code.get_regd_codeid_by_type(RpcRecv)).unwrap()
    msg = recv["msg"]
    assert msg["errcode"] == "val_err"
    assert msg["msg"] == "whoops"

    await app.destroy()
    assert destroy_flag
    con_task.cancel()

async def test_sys():
    init_flag = False
    destroy_flag = False
    sys_flag = False

    async def sys_test(inp: SysInp[Mock_1, MockCfg]) -> Res[SysInp]:
        assert inp.msg.key == "hello"
        nonlocal sys_flag
        sys_flag = True
        return inp.ok()

    async def _init(inp: PluginInp[MockCfg]) -> Res[None]:
        nonlocal init_flag
        init_flag = True
        return Ok(None)

    async def _destroy(inp: PluginInp[MockCfg]) -> Res[None]:
        nonlocal destroy_flag
        destroy_flag = True
        return Ok(None)

    plugin = Plugin(
        name="test",
        cfgtype=MockCfg,
        init=_init,
        destroy=_destroy,
        sys=[SysSpec.new(Mock_1, sys_test)]
    )
    app = await App().init(AppCfg(
        bus_cfg=BusCfg(
            transports=[
                Transport(is_server=True, con_type=MockCon)
            ]
        ),
        plugins=[plugin],
        extend_cfg_pack={
            "test": [
                MockCfg(num=1)
            ]
        }
    ))
    assert init_flag
    assert not destroy_flag

    con = MockCon()
    con_task = asyncio.create_task(app.get_bus().unwrap().con(con))
    await con.client_recv()
    send_msid = uuid4()
    await con.client_send({
        "sid": send_msid,
        "codeid": (await Code.get_regd_codeid_by_type(Mock_1)).unwrap(),
        "msg": {
            "key": "hello"
        }
    })
    await asyncio.sleep(0.1)
    assert sys_flag
    recv = await asyncio.wait_for(con.client_recv(), 1)
    assert "msg" not in recv
    assert recv["lsid"] == send_msid
    assert recv["codeid"] \
        == (await Code.get_regd_codeid_by_type(ok)).unwrap()

    await app.destroy()
    assert destroy_flag
    con_task.cancel()

async def test_sys_err():
    init_flag = False
    destroy_flag = False
    sys_flag = False

    async def sys_test(inp: SysInp[Mock_1, MockCfg]):
        assert inp.msg.key == "hello"
        nonlocal sys_flag
        sys_flag = True
        return Err("whoops")

    async def _init(inp: PluginInp[MockCfg]) -> Res[None]:
        nonlocal init_flag
        init_flag = True
        return Ok(None)

    async def _destroy(inp: PluginInp[MockCfg]) -> Res[None]:
        nonlocal destroy_flag
        destroy_flag = True
        return Ok(None)

    plugin = Plugin(
        name="test",
        cfgtype=MockCfg,
        init=_init,
        destroy=_destroy,
        sys=[SysSpec.new(Mock_1, sys_test)]
    )
    app = await App().init(AppCfg(
        bus_cfg=BusCfg(
            transports=[
                Transport(is_server=True, con_type=MockCon)
            ]
        ),
        plugins=[plugin],
        extend_cfg_pack={
            "test": [
                MockCfg(num=1)
            ]
        }
    ))
    assert init_flag
    assert not destroy_flag

    con = MockCon()
    con_task = asyncio.create_task(app.get_bus().unwrap().con(con))
    await con.client_recv()
    send_msid = uuid4()
    await con.client_send({
        "sid": send_msid,
        "codeid": (await Code.get_regd_codeid_by_type(Mock_1)).unwrap(),
        "msg": {
            "key": "hello"
        }
    })
    await asyncio.sleep(0.1)
    assert sys_flag
    recv = await asyncio.wait_for(con.client_recv(), 1)
    assert recv["lsid"] == send_msid
    assert recv["codeid"] \
        == (await Code.get_regd_codeid_by_type(ValErr)).unwrap()
    msg = recv["msg"]
    assert msg["errcode"] == "val_err"
    assert msg["msg"] == "whoops"

    await app.destroy()
    assert destroy_flag
    con_task.cancel()
