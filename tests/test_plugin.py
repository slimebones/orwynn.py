import asyncio
from pykit.code import Code
from pykit.res import Ok, Res
from pykit.uuid import uuid4
from rxcat import EmptyRpcArgs, ServerBusCfg, Transport, SrpcSend

from orwynn import App, AppCfg, Plugin, SysArgs
from tests.conftest import Mock_1, MockCfg, MockConn


async def test_main():
    init_flag = False
    destroy_flag = False
    rpc_flag = False

    async def rsys__test(args: SysArgs[MockCfg], body: Mock_1):
        assert body.key == "hello"
        nonlocal rpc_flag
        rpc_flag = True

    async def _init(args: SysArgs[MockCfg]) -> Res[None]:
        nonlocal init_flag
        init_flag = True
        return Ok(None)

    async def _destroy(args: SysArgs[MockCfg]) -> Res[None]:
        nonlocal destroy_flag
        destroy_flag = True
        return Ok(None)

    plugin = Plugin(
        name="test", cfgtype=MockCfg, init=_init, destroy=_destroy)
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

    assert rpc_flag
    conn = MockConn()
    conn_task = asyncio.create_task(app.get_bus().eject().conn(conn))
    await conn.client__recv()
    await conn.client__send({
        "sid": uuid4(),
        "bodycodeid": (await Code.get_regd_codeid_by_type(SrpcSend)),
        "body": {
            "key": ""
        }
    })

    await app.destroy()
    assert destroy_flag
    conn_task.cancel()
