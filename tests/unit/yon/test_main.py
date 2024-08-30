import asyncio

from ryz.core import Code, Err, Ok, Res, ecode
from ryz.uuid import uuid4

from orwynn.yon.server import (
    Bus,
    ConArgs,
    PubOpts,
    StaticCodeid,
)
from tests.unit.yon.conftest import (
    EmptyMock,
    Mock_1,
    Mock_2,
    MockCon,
)


async def test_pubsub(bus: Bus):
    flag = False

    async def sub_mock_1(msg: Mock_1) -> Res[None]:
        assert isinstance(msg, Mock_1)
        assert msg.num == 1
        nonlocal flag
        flag = True
        return Ok()

    _ = (await bus.sub(Mock_1, sub_mock_1)).unwrap()
    (await bus.pub(Mock_1(num=1))).unwrap()

    assert flag

async def test_data_static_indexes(bus: Bus):
    codes = (await Code.get_regd_codes()).unwrap()
    assert codes[0] == "yon::server::welcome"
    assert codes[1] == "yon::ok"

async def test_pubsub_err(bus: Bus):
    flag = False

    async def sub_test(msg: Err) -> Res[None]:
        assert msg.is_(ecode.Val)
        assert msg.msg == "hello"
        nonlocal flag
        flag = True
        return Ok()

    _ = (await bus.sub(ecode.Val, sub_test)).unwrap()
    (await bus.pub(Err("hello", ecode.Val))).unwrap()
    assert flag

async def test_pubr(bus: Bus):
    async def sub_test(msg: Err) -> Res[Mock_1]:
        assert msg.is_(ecode.Val)
        assert msg.msg == "hello"
        return Ok(Mock_1(num=1))

    _ = (await bus.sub(ecode.Val, sub_test)).unwrap()
    response = (await bus.pubr(
        Err("hello", ecode.Val), PubOpts(pubr_timeout=1)
    )).unwrap()
    assert type(response) is Mock_1
    assert response.num == 1

async def test_lsid_net(bus: Bus):
    """
    Tests correctness of published back to net responses.
    """
    async def sub_test(msg: Mock_1):
        await bus.pub(Mock_2(num=2), PubOpts(lsid=bus.get_ctx_msid().unwrap()))
        return Ok(Mock_2(num=3))

    await bus.sub(Mock_1, sub_test)
    con = MockCon(ConArgs(core=None))
    con_task = asyncio.create_task(bus.con(con))

    await asyncio.wait_for(con.client__recv(), 1)
    await con.client__send({
        "sid": uuid4(),
        "codeid": (await Code.get_regd_codeid_by_type(Mock_1)).unwrap(),
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

async def test_recv_empty_data(bus: Bus):
    """
    Should validate empty data rbmsg, or data set to None to empty base models
    """
    async def sub_test(msg: EmptyMock) -> Res[None]:
        return Ok()

    _ = (await bus.sub(EmptyMock, sub_test)).unwrap()
    con = MockCon(ConArgs(core=None))
    con_task = asyncio.create_task(bus.con(con))

    await asyncio.wait_for(con.client__recv(), 1)
    await con.client__send({
        "sid": uuid4(),
        "codeid": (await Code.get_regd_codeid_by_type(EmptyMock)).unwrap()
    })
    response = await asyncio.wait_for(con.client__recv(), 1)
    assert response["codeid"] == StaticCodeid.Ok

    con_task.cancel()

async def test_send_empty_data(bus: Bus):
    """
    Should validate empty data rbmsg, or data set to None to empty base models
    """
    async def sub_test(msg: Mock_1):
        return Ok(EmptyMock())

    await bus.sub(Mock_1, sub_test)
    con = MockCon(ConArgs(core=None))
    con_task = asyncio.create_task(bus.con(con))

    await asyncio.wait_for(con.client__recv(), 1)
    await con.client__send({
        "sid": uuid4(),
        "codeid": (await Code.get_regd_codeid_by_type(Mock_1)).unwrap(),
        "msg": {
            "num": 1
        }
    })
    response = await asyncio.wait_for(con.client__recv(), 1)
    assert \
        response["codeid"] \
        == (await Code.get_regd_codeid_by_type(EmptyMock)).unwrap()
    assert "data" not in response

    con_task.cancel()
