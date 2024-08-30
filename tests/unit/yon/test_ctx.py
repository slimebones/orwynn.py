import asyncio

from ryz.code import Code
from ryz.res import Ok, Res
from ryz.uuid import uuid4
from yon.server import (
    Bus,
    BusCfg,
    ConArgs,
    EmptyRpcArgs,
    RpcRecv,
    RpcSend,
    Transport,
    ok,
)

from tests.unit.yon.conftest import (
    Mock_1,
    MockCon,
    get_mock_ctx_manager_for_msg,
    yon_mock_ctx,
)


async def test_subfn(sbus: Bus):
    con = MockCon(ConArgs(core=None))
    async def sub_f(msg: Mock_1):
        assert sbus.get_ctx()["consid"] == con.sid

    await sbus.sub(Mock_1, sub_f)
    con_task = asyncio.create_task(sbus.con(con))
    # recv welcome
    await asyncio.wait_for(con.client__recv(), 1)
    await con.client__send({
        "sid": uuid4(),
        "codeid": (await Code.get_regd_codeid_by_type(Mock_1)).eject(),
        "msg": {
            "num": 1
        }
    })
    rbmsg = await asyncio.wait_for(con.client__recv(), 1)
    assert \
        rbmsg["codeid"] == (await Code.get_regd_codeid_by_type(ok)).eject()
    con_task.cancel()

async def test_rpc(sbus: Bus):
    con = MockCon(ConArgs(core=None))
    async def rpc_update_email(msg: EmptyRpcArgs) -> Res[int]:
        assert sbus.get_ctx()["consid"] == con.sid
        return Ok(0)

    con_task = asyncio.create_task(sbus.con(con))
    # recv welcome
    await asyncio.wait_for(con.client__recv(), 1)
    rpckey = "update_email"
    Bus.reg_rpc(rpckey, rpc_update_email).eject()
    await con.client__send({
        "sid": uuid4(),
        "codeid": (await Code.get_regd_codeid_by_type(RpcSend)).eject(),
        "msg": {
            "key": rpckey,
            "data": {"username": "test_username", "email": "test_email"}
        }
    })
    rbmsg = await asyncio.wait_for(con.client__recv(), 1)
    assert rbmsg["codeid"] == \
        (await Code.get_regd_codeid_by_type(RpcRecv)).eject()

    con_task.cancel()

async def test_sub_custom_ctx_manager():
    sbus = Bus.ie()
    await sbus.init(BusCfg(sub_ctxfn=get_mock_ctx_manager_for_msg))

    async def sub_f(msg: Mock_1):
        assert yon_mock_ctx.get()["name"] == "hello"

    await sbus.sub(Mock_1, sub_f)
    await sbus.pubr(Mock_1(num=1))

async def test_rpc_custom_ctx_manager():
    sbus = Bus.ie()
    await sbus.init(BusCfg(
        transports=[
            Transport(
                is_server=True,
                con_type=MockCon)
        ],
        sub_ctxfn=get_mock_ctx_manager_for_msg))

    con = MockCon(ConArgs(core=None))
    async def rpc_update_email(msg: EmptyRpcArgs) -> Res[int]:
        assert yon_mock_ctx.get()["name"] == "hello"
        return Ok(0)

    con_task = asyncio.create_task(sbus.con(con))
    # recv welcome
    await asyncio.wait_for(con.client__recv(), 1)
    rpckey = "update_email"
    Bus.reg_rpc(rpckey, rpc_update_email).eject()
    await con.client__send({
        "sid": uuid4(),
        "codeid": (await Code.get_regd_codeid_by_type(RpcSend)).eject(),
        "msg": {
            "key": rpckey,
            "data": {}
        }
    })
    rbmsg = await asyncio.wait_for(con.client__recv(), 1)
    assert rbmsg["codeid"] == \
        (await Code.get_regd_codeid_by_type(RpcRecv)).eject()

    con_task.cancel()
