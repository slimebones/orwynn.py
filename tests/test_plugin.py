import asyncio

from ryz.code import Code
from ryz.err import ValErr
from ryz.res import Ok, Res, valerr
from ryz.uuid import uuid4
from yon import ServerBusCfg, SrpcRecv, SrpcSend, Transport, ok

from orwynn import App, AppCfg, Plugin, SysArgs
from tests.conftest import Mock_1, MockCfg, MockCon


async def test_rsys():
    init_flag = False
    destroy_flag = False
    rpc_flag = False

    async def rsys__test(args: SysArgs[MockCfg], body: Mock_1) -> Res[None]:
        assert body.key == "hello"
        nonlocal rpc_flag
        rpc_flag = True
        return Ok(None)

    async def _init(args: SysArgs[MockCfg]) -> Res[None]:
        nonlocal init_flag
        init_flag = True
        return Ok(None)

    async def _destroy(args: SysArgs[MockCfg]) -> Res[None]:
        nonlocal destroy_flag
        destroy_flag = True
        return Ok(None)

    plugin = Plugin(
        name="test",
        cfgtype=MockCfg,
        init=_init,
        destroy=_destroy,
        rsys=[rsys__test])
    app = await App().init(AppCfg(
        server_bus_cfg=ServerBusCfg(
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
    con_task = asyncio.create_task(app.get_bus().eject().con(con))
    await con.client__recv()
    send_msid = uuid4()
    await con.client__send({
        "sid": send_msid,
        "bodycodeid": (await Code.get_regd_codeid_by_type(SrpcSend)).eject(),
        "body": {
            "key": "test::test",
            "body": {
                "key": "hello"
            }
        }
    })
    await asyncio.sleep(0.1)
    assert rpc_flag
    recv = await asyncio.wait_for(con.client__recv(), 1)
    assert "body" not in recv
    assert recv["lsid"] == send_msid
    assert recv["bodycodeid"] \
        == (await Code.get_regd_codeid_by_type(SrpcRecv)).eject()

    await app.destroy()
    assert destroy_flag
    con_task.cancel()

async def test_rsys_err():
    init_flag = False
    destroy_flag = False
    rpc_flag = False

    async def rsys__test(args: SysArgs[MockCfg], body: Mock_1) -> Res[None]:
        assert body.key == "hello"
        nonlocal rpc_flag
        rpc_flag = True
        return valerr("whoops")

    async def _init(args: SysArgs[MockCfg]) -> Res[None]:
        nonlocal init_flag
        init_flag = True
        return Ok(None)

    async def _destroy(args: SysArgs[MockCfg]) -> Res[None]:
        nonlocal destroy_flag
        destroy_flag = True
        return Ok(None)

    plugin = Plugin(
        name="test",
        cfgtype=MockCfg,
        init=_init,
        destroy=_destroy,
        rsys=[rsys__test])
    app = await App().init(AppCfg(
        server_bus_cfg=ServerBusCfg(
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
    con_task = asyncio.create_task(app.get_bus().eject().con(con))
    await con.client__recv()
    send_msid = uuid4()
    await con.client__send({
        "sid": send_msid,
        "bodycodeid": (await Code.get_regd_codeid_by_type(SrpcSend)).eject(),
        "body": {
            "key": "test::test",
            "body": {
                "key": "hello"
            }
        }
    })
    await asyncio.sleep(0.1)
    assert rpc_flag
    recv = await asyncio.wait_for(con.client__recv(), 1)
    assert recv["lsid"] == send_msid
    assert recv["bodycodeid"] \
        == (await Code.get_regd_codeid_by_type(SrpcRecv)).eject()
    body = recv["body"]
    assert body["errcode"] == "val_err"
    assert body["msg"] == "whoops"

    await app.destroy()
    assert destroy_flag
    con_task.cancel()

async def test_sys():
    init_flag = False
    destroy_flag = False
    sys_flag = False

    async def sys__test(args: SysArgs[MockCfg], body: Mock_1):
        assert body.key == "hello"
        nonlocal sys_flag
        sys_flag = True

    async def _init(args: SysArgs[MockCfg]) -> Res[None]:
        nonlocal init_flag
        init_flag = True
        return Ok(None)

    async def _destroy(args: SysArgs[MockCfg]) -> Res[None]:
        nonlocal destroy_flag
        destroy_flag = True
        return Ok(None)

    plugin = Plugin(
        name="test",
        cfgtype=MockCfg,
        init=_init,
        destroy=_destroy,
        sys=[sys__test])
    app = await App().init(AppCfg(
        server_bus_cfg=ServerBusCfg(
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
    con_task = asyncio.create_task(app.get_bus().eject().con(con))
    await con.client__recv()
    send_msid = uuid4()
    await con.client__send({
        "sid": send_msid,
        "bodycodeid": (await Code.get_regd_codeid_by_type(Mock_1)).eject(),
        "body": {
            "key": "hello"
        }
    })
    await asyncio.sleep(0.1)
    assert sys_flag
    recv = await asyncio.wait_for(con.client__recv(), 1)
    assert "body" not in recv
    assert recv["lsid"] == send_msid
    assert recv["bodycodeid"] \
        == (await Code.get_regd_codeid_by_type(ok)).eject()

    await app.destroy()
    assert destroy_flag
    con_task.cancel()

async def test_sys_err():
    init_flag = False
    destroy_flag = False
    sys_flag = False

    async def sys__test(args: SysArgs[MockCfg], body: Mock_1):
        assert body.key == "hello"
        nonlocal sys_flag
        sys_flag = True
        return valerr("whoops")

    async def _init(args: SysArgs[MockCfg]) -> Res[None]:
        nonlocal init_flag
        init_flag = True
        return Ok(None)

    async def _destroy(args: SysArgs[MockCfg]) -> Res[None]:
        nonlocal destroy_flag
        destroy_flag = True
        return Ok(None)

    plugin = Plugin(
        name="test",
        cfgtype=MockCfg,
        init=_init,
        destroy=_destroy,
        sys=[sys__test])
    app = await App().init(AppCfg(
        server_bus_cfg=ServerBusCfg(
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
    con_task = asyncio.create_task(app.get_bus().eject().con(con))
    await con.client__recv()
    send_msid = uuid4()
    await con.client__send({
        "sid": send_msid,
        "bodycodeid": (await Code.get_regd_codeid_by_type(Mock_1)).eject(),
        "body": {
            "key": "hello"
        }
    })
    await asyncio.sleep(0.1)
    assert sys_flag
    recv = await asyncio.wait_for(con.client__recv(), 1)
    assert recv["lsid"] == send_msid
    assert recv["bodycodeid"] \
        == (await Code.get_regd_codeid_by_type(ValErr)).eject()
    body = recv["body"]
    assert body["errcode"] == "val_err"
    assert body["msg"] == "whoops"

    await app.destroy()
    assert destroy_flag
    con_task.cancel()
