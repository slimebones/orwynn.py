import asyncio
from typing import Any

from pydantic import BaseModel
from ryz.code import Code
from ryz.err import ValErr
from ryz.err_utils import get_err_msg
from ryz.res import Err, Ok, valerr
from ryz.uuid import uuid4
from yon.server import (
    Bus,
    BusCfg,
    ConArgs,
    InterruptPipeline,
    Msg,
    PubList,
    PubOpts,
    StaticCodeid,
    Transport,
    sub,
)

from tests.unit.yon.conftest import (
    EmptyMock,
    Mock_1,
    Mock_2,
    MockCon,
)


async def test_pubsub(sbus: Bus):
    flag = False

    async def sub_mock_1(msg: Mock_1):
        assert isinstance(msg, Mock_1)
        assert msg.num == 1
        nonlocal flag
        flag = True

    (await sbus.sub(Mock_1, sub_mock_1)).eject()
    (await sbus.pub(Mock_1(num=1))).eject()

    assert flag

async def test_data_static_indexes(sbus: Bus):
    codes = (await Code.get_regd_codes()).eject()
    assert codes[0] == "yon::server::welcome"
    assert codes[1] == "yon::ok"

async def test_pubsub_err(sbus: Bus):
    flag = False

    async def sub_test(msg: ValErr):
        assert type(msg) is ValErr
        assert get_err_msg(msg) == "hello"
        nonlocal flag
        flag = True

    (await sbus.sub(ValErr, sub_test)).eject()
    (await sbus.pub(ValErr("hello"))).eject()
    assert flag

async def test_pubr(sbus: Bus):
    async def sub_test(msg: ValErr):
        assert type(msg) is ValErr
        assert get_err_msg(msg) == "hello"
        return Ok(Mock_1(num=1))

    (await sbus.sub(ValErr, sub_test)).eject()
    response = (await sbus.pubr(
        ValErr("hello"), PubOpts(pubr_timeout=1))).eject()
    assert type(response) is Mock_1
    assert response.num == 1

async def test_lsid_net(sbus: Bus):
    """
    Tests correctness of published back to net responses.
    """
    async def sub_test(msg: Mock_1):
        return Ok(PubList([Mock_2(num=2), Mock_2(num=3)]))

    await sbus.sub(Mock_1, sub_test)
    con = MockCon(ConArgs(core=None))
    con_task = asyncio.create_task(sbus.con(con))

    await asyncio.wait_for(con.client__recv(), 1)
    await con.client__send({
        "sid": uuid4(),
        "codeid": (await Code.get_regd_codeid_by_type(Mock_1)).eject(),
        "msg": {
            "num": 1
        }
    })
    await asyncio.sleep(0.1)
    count = 0
    while not con.out_queue.empty():
        response = await asyncio.wait_for(con.client__recv(), 1)
        response_data = response["msg"]
        count += 1
        if count == 1:
            assert response_data["num"] == 2
        elif count == 2:
            assert response_data["num"] == 3
        else:
            raise AssertionError
    assert count == 2

    con_task.cancel()

async def test_recv_empty_data(sbus: Bus):
    """
    Should validate empty data rbmsg, or data set to None to empty base models
    """
    async def sub_test(msg: EmptyMock):
        return

    await sbus.sub(EmptyMock, sub_test)
    con = MockCon(ConArgs(core=None))
    con_task = asyncio.create_task(sbus.con(con))

    await asyncio.wait_for(con.client__recv(), 1)
    await con.client__send({
        "sid": uuid4(),
        "codeid": (await Code.get_regd_codeid_by_type(EmptyMock)).eject()
    })
    response = await asyncio.wait_for(con.client__recv(), 1)
    assert response["codeid"] == StaticCodeid.Ok

    con_task.cancel()

async def test_send_empty_data(sbus: Bus):
    """
    Should validate empty data rbmsg, or data set to None to empty base models
    """
    async def sub_test(msg: Mock_1):
        return Ok(EmptyMock())

    await sbus.sub(Mock_1, sub_test)
    con = MockCon(ConArgs(core=None))
    con_task = asyncio.create_task(sbus.con(con))

    await asyncio.wait_for(con.client__recv(), 1)
    await con.client__send({
        "sid": uuid4(),
        "codeid": (await Code.get_regd_codeid_by_type(Mock_1)).eject(),
        "msg": {
            "num": 1
        }
    })
    response = await asyncio.wait_for(con.client__recv(), 1)
    assert \
        response["codeid"] \
        == (await Code.get_regd_codeid_by_type(EmptyMock)).eject()
    assert "data" not in response

    con_task.cancel()

async def test_global_subfn_conditions():
    async def condition(data: Msg) -> bool:
        return data.num == 0

    flag = False
    async def sub_test(msg: Mock_1):
        # only mocks with num=0 should be passed
        assert msg.num == 0
        nonlocal flag
        assert not flag
        flag = True

    sbus = Bus.ie()
    cfg = BusCfg(
        reg_types={Mock_1},
        global_subfn_conditions=[condition])
    await sbus.init(cfg)

    (await sbus.sub(Mock_1, sub_test)).eject()
    (await sbus.pub(Mock_1(num=1))).eject()

async def test_auth_example():
    """
    Should validate empty data rbmsg, or data set to None to empty base models
    """
    class Login(BaseModel):
        username: str

        @staticmethod
        def code():
            return "login"

    class Logout(BaseModel):
        @staticmethod
        def code():
            return "logout"

    async def ifilter__auth(data: Msg) -> Msg:
        sbus = Bus.ie()
        consid_res = sbus.get_ctx_consid()
        # skip inner messages
        if isinstance(consid_res, Err) or not consid_res.okval:
            return data

        consid = consid_res.okval
        tokens = sbus.get_con_tokens(consid).eject()
        # if data is mock_1, the con must have tokens
        if isinstance(data, Mock_1) and not tokens:
            return InterruptPipeline(ValErr("forbidden"))
        return data

    async def sub_login(msg: Login):
        if msg.username == "right":
            Bus.ie().set_ctx_con_tokens(["right"])
            return None
        return valerr(f"wrong username {msg.username}")

    async def sub_logout(msg: Logout):
        Bus.ie().set_ctx_con_tokens([])

    async def sub_mock_1(msg: Mock_1):
        return

    sbus = Bus.ie()
    cfg = BusCfg(
        transports=[
            Transport(
                is_server=True,
                con_type=MockCon)
        ],
        reg_types={Mock_1, Mock_2, Login, Logout},
        global_subfn_inp_filters={ifilter__auth}
    )
    await sbus.init(cfg)

    (await sbus.reg_types({Login, Logout})).eject()
    (await sbus.sub(Login, sub_login)).eject()
    (await sbus.sub(Logout, sub_logout)).eject()
    (await sbus.sub(Mock_1, sub_mock_1)).eject()

    con = MockCon(ConArgs(core=None))
    con_task = asyncio.create_task(sbus.con(con))

    await asyncio.wait_for(con.client__recv(), 1)
    mock_1_codeid = (await Code.get_regd_codeid_by_type(Mock_1)).eject()
    valerr_codeid = (await Code.get_regd_codeid_by_type(ValErr)).eject()
    login_codeid = (await Code.get_regd_codeid_by_type(Login)).eject()
    logout_codeid = (await Code.get_regd_codeid_by_type(Logout)).eject()

    # unregistered mock_1
    await con.client__send({
        "sid": uuid4(),
        "codeid": mock_1_codeid,
        "msg": {
            "num": 1
        }
    })
    response = await asyncio.wait_for(con.client__recv(), 1)
    assert response["codeid"] == valerr_codeid
    assert response["msg"]["msg"] == "forbidden"

    # register wrong username
    await con.client__send({
        "sid": uuid4(),
        "codeid": login_codeid,
        "msg": {
            "username": "wrong"
        }
    })
    response = await asyncio.wait_for(con.client__recv(), 1)
    assert response["codeid"] == valerr_codeid
    assert response["msg"]["msg"] == "wrong username wrong"

    # register right username
    await con.client__send({
        "sid": uuid4(),
        "codeid": login_codeid,
        "msg": {
            "username": "right"
        }
    })
    response = await asyncio.wait_for(con.client__recv(), 1)
    assert response["codeid"] == StaticCodeid.Ok
    assert "right" in con.get_tokens(), "does not contain registered token"

    # registered mock_1
    await con.client__send({
        "sid": uuid4(),
        "codeid": mock_1_codeid,
        "msg": {
            "num": 1
        }
    })
    response = await asyncio.wait_for(con.client__recv(), 1)
    assert response["codeid"] == StaticCodeid.Ok

    # logout
    await con.client__send({
        "sid": uuid4(),
        "codeid": logout_codeid
    })
    response = await asyncio.wait_for(con.client__recv(), 1)
    assert response["codeid"] == StaticCodeid.Ok
    assert not con.get_tokens()

    con_task.cancel()

async def test_sub_decorator():
    class Mock(BaseModel):
        @staticmethod
        def code():
            return "mock"

    @sub(Mock)
    def sub_t(msg: Mock) -> Any:
        return

    sbus = Bus.ie()
    await sbus.init(BusCfg(reg_types={Mock}))
    assert Mock.code() in sbus._code_to_subfns
