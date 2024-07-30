from rxcat import ServerBus, ok, PubOpts
from orwynn import App, SysArgs, sys, AppCfg
from tests.conftest import Mock_1, MockCfg


async def test_main(app_cfg: AppCfg):
    @sys(MockCfg)
    async def sys__mock(args: SysArgs[MockCfg], body: Mock_1):
        assert body.key == "hello"

    await App().init(app_cfg)

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
