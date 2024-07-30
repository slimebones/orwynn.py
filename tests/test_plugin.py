from pykit.res import Ok, Res
from rxcat import ServerBusCfg, Transport

from orwynn import App, AppCfg, Plugin, SysArgs
from tests.conftest import MockCfg, MockConn


async def test_main():
    init_flag = False
    destroy_flag = False

    async def _init(args: SysArgs[MockCfg]) -> Res[None]:
        nonlocal init_flag
        init_flag = True
        return Ok(None)
    async def _destroy(args: SysArgs[MockCfg]) -> Res[None]:
        nonlocal destroy_flag
        destroy_flag = True
        return Ok(None)

    plugin = Plugin(
        name="test_plugin", cfgtype=MockCfg, init=_init, destroy=_destroy)
    app = await App().init(AppCfg(
        server_bus_cfg=ServerBusCfg(
            transports=[
                Transport(is_server=True, conn_type=MockConn)
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

    await app.destroy(is_hard=True)
    assert destroy_flag
