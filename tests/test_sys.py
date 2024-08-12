from yon.server import PubOpts, Bus, ok

from orwynn import App, AppCfg, Plugin, SysArgs, SysSpec
from tests.conftest import Mock_1, MockCfg


async def test_main(app_cfg: AppCfg):
    async def sys_mock(msg: Mock_1, args: SysArgs[MockCfg]):
        assert msg.key == "hello"

    plugin = Plugin(
        name="test",
        cfgtype=MockCfg,
        sys=[SysSpec.new(Mock_1, sys_mock)]
    )
    app_cfg.plugins.append(plugin)
    await App().init(app_cfg)

    r = (await Bus.ie().pubr(
        Mock_1(key="hello"), PubOpts(pubr_timeout=1))).eject()
    assert isinstance(r, ok)


async def test_incorrect_name(app_cfg: AppCfg):
    async def whocares__mock(msg: Mock_1, args: SysArgs[MockCfg]):
        assert msg.key == "hello"

    plugin = Plugin(
        name="test", cfgtype=MockCfg, sys=[SysSpec.new(Mock_1, whocares__mock)]
    )
    app_cfg.plugins.append(plugin)
    await App().init(app_cfg)

    try:
        (await Bus.ie().pubr(
            Mock_1(key="hello"), PubOpts(pubr_timeout=0.2))).eject()
    except TimeoutError:
        # no systems were registered => ok
        pass
    else:
        raise AssertionError
