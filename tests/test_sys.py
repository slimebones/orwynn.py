from yon.server import Bus, PubOpts, ok

from orwynn import App, AppCfg, Plugin, SysInp, SysSpec
from tests.conftest import Mock_1, MockCfg
from ryz.res import Res


async def test_main(app_cfg: AppCfg):
    async def sys_mock(inp: SysInp[Mock_1, MockCfg]) -> Res[SysInp]:
        assert inp.msg.key == "hello"
        return inp.ok()

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
    async def mock(inp: SysInp[Mock_1, MockCfg]) -> Res[SysInp]:
        assert inp.msg.key == "hello"
        return inp.ok()

    plugin = Plugin(
        name="test", cfgtype=MockCfg, sys=[SysSpec.new(Mock_1, mock)]
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
