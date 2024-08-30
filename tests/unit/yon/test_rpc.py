import asyncio
from typing import Any

from pydantic import BaseModel
from ryz.core import get_fqname
from ryz.core import ValErr
from ryz.core import Err, Ok, Res
from ryz.uuid import uuid4
from yon.server import Bus, ConArgs, rpc

from tests.unit.yon.conftest import (
    EmptyMock,
    MockCon,
    find_codeid_in_welcome_rbmsg,
)


async def test_main(sbus: Bus):
    class UpdEmailArgs(BaseModel):
        username: str
        email: str
    async def rpc_update_email(msg: UpdEmailArgs) -> Res[int]:
        username = msg.username
        email = msg.email
        if username == "throw":
            return Err("hello"))
        assert username == "test_username"
        assert email == "test_email"
        return Ok(0)

    con_1 = MockCon(ConArgs(
        core=None))
    con_task_1 = asyncio.create_task(sbus.con(con_1))

    welcome_rbmsg = await asyncio.wait_for(con_1.client__recv(), 1)
    yon_rpc_req_codeid = find_codeid_in_welcome_rbmsg(
        "yon::server::rpc_send", welcome_rbmsg).unwrap()

    rpckey = "update_email"
    Bus.reg_rpc(rpckey, rpc_update_email).unwrap()

    await con_1.client__send({
        "sid": uuid4(),
        "codeid": yon_rpc_req_codeid,
        "msg": {
            "key": rpckey,
            "data": {"username": "test_username", "email": "test_email"}
        }
    })
    rpc_rbmsg = await asyncio.wait_for(con_1.client__recv(), 1)
    rpc_msg = rpc_rbmsg["msg"]
    assert rpc_msg == 0

    rpckey = "update_email"
    send_msid = uuid4()
    await con_1.client__send({
        "sid": send_msid,
        "codeid": yon_rpc_req_codeid,
        "msg": {
            "key": rpckey,
            "data": {"username": "throw", "email": "test_email"}
        }
    })
    rpc_rbmsg = await asyncio.wait_for(con_1.client__recv(), 1)
    assert rpc_rbmsg["lsid"] == send_msid
    rpc_msg = rpc_rbmsg["msg"]
    assert rpc_msg["errcode"] == ValErr.code()
    assert rpc_msg["msg"] == "hello"
    assert rpc_msg["name"] == get_fqname(ValErr())

    con_task_1.cancel()

async def test_srpc_decorator():
    @rpc("test")
    async def rpc_test(msg: EmptyMock) -> Res[Any]:
        return Ok(None)
    bus = Bus.ie()
    await bus.init()
    assert "test" in bus._rpckey_to_fn

async def test_reg_custom_rpc_key():
    async def rpc_test(msg: EmptyMock) -> Res[Any]:
        return Ok(None)
    bus = Bus.ie()
    await bus.init()
    bus.reg_rpc("whocares", rpc_test).unwrap()
    assert "whocares" in bus._rpckey_to_fn

async def test_provide_custom_msgtype():
    class Something(BaseModel):
        pass

    async def rpc_test(msg: Something) -> Res[None]:
        return Ok()

    bus = Bus.ie()
    await bus.init()
    bus.reg_rpc("test", rpc_test, Something).unwrap()
    assert bus._rpckey_to_fn["test"] == (rpc_test, Something)

async def test_provide_custom_msgtype_wrong():
    class Something(BaseModel):
        pass

    async def rpc_test(msg: Something) -> Res[None]:
        return Ok()

    bus = Bus.ie()
    await bus.init()
    r = bus.reg_rpc("test", rpc_test, int)  # type: ignore
    assert isinstance(r, Err)
    assert "test" not in bus._rpckey_to_fn
