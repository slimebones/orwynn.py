from rxcat import ConnArgs, ServerBus, ok, PubOpts
from orwynn import App, SysArgs, rpcsys, sys, AppCfg
from tests.conftest import Mock_1, MockCfg, MockConn
from pykit.uuid import uuid4


async def test_main(app_cfg: AppCfg):
    @rpcsys(MockCfg)
    async def sys__mock(args: SysArgs[MockCfg], body: Mock_1):
        assert body.key == "hello"

    app = await App().init(app_cfg)
    bus = app.get_bus().eject()
    conn = MockConn()
    await bus.conn(conn)
    await conn.client__send({
        "sid": uuid4(),
        "key": "mock::" + uuid4(),
        "body": {
        }
    })

    r = (await ServerBus.ie().pubr(
        Mock_1(key="hello"), PubOpts(pubr__timeout=1))).eject()
    assert isinstance(r, ok)


async def test_incorrect_name(app_cfg: AppCfg):
    @sys(MockCfg)
    async def whocares__mock(args: SysArgs[MockCfg], body: Mock_1):
        assert body.key == "hello"

    await App().init(app_cfg)

    try:
        (await ServerBus.ie().pubr(
            Mock_1(key="hello"), PubOpts(pubr__timeout=0.2))).eject()
    except TimeoutError:
        # no systems were registered => ok
        pass
    else:
        raise AssertionError
