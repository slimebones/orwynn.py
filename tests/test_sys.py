import asyncio
from yon.server import Bus, PubOpts, ok

from orwynn import App, AppCfg, GlobalSysOpts, Plugin, RsysSpec, SysInp, SysOpts, SysSpec
from orwynn._pepel import AsyncPipeline
from tests.conftest import Mock_1, MockCfg, MockCon
from ryz.res import Res, Ok
from ryz.code import Code
from ryz.uuid import uuid4


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

async def test_pipeline(app_cfg: AppCfg):
    async def add_str(inp: SysInp[Mock_1, MockCfg]) -> Res[SysInp]:
        inp.msg.key += "h"
        return Ok(inp)

    async def rpc_mock(inp: SysInp[Mock_1, MockCfg]) -> Res[SysInp]:
        assert inp.msg.key.startswith("start-")
        assert inp.msg.key.count("h") == 6
        return inp.ok()

    plugin = Plugin(
        name="test",
        cfgtype=MockCfg,
        rsys=[
            RsysSpec.new(
                "mock",
                Mock_1,
                rpc_mock,
                SysOpts(pipeline_before=AsyncPipeline())
            )
        ],
        global_opts=GlobalSysOpts(
            all=SysOpts(
                pipeline_before=AsyncPipeline(add_str, add_str),
            ),
            sys=SysOpts(
                pipeline_before=AsyncPipeline(add_str, add_str),
            ),
            rsys=SysOpts(
                pipeline_before=AsyncPipeline(add_str, add_str)
            )
        )
    )
    app_cfg.global_opts.all.pipeline_before = AsyncPipeline(add_str, add_str)
    app_cfg.global_opts.sys.pipeline_before = AsyncPipeline(add_str, add_str)
    app_cfg.global_opts.rsys.pipeline_before = AsyncPipeline(add_str, add_str)

    app_cfg.global_opts.all.pipeline_after = AsyncPipeline(add_str, add_str)
    app_cfg.global_opts.sys.pipeline_after = AsyncPipeline(add_str, add_str)
    app_cfg.global_opts.rsys.pipeline_after = AsyncPipeline(add_str, add_str)

    app_cfg.plugins.append(plugin)
    app = await App().init(app_cfg)

    con = MockCon()
    con_task = asyncio.create_task(app.get_bus().eject().con(con))
    await con.client_recv()
    await con.client_send({
        "sid": uuid4(),
        "codeid": (await Code.get_regd_codeid_by_type(Mock_1)).eject(),
        "msg": {
            "key": "test::mock",
            "data": {
                "key": "start-"
            }
        }
    })
    out = Mock_1.model_validate((await con.client_recv())["msg"]["data"])
    assert out.key.startswith("start-")
    assert out.key.count("h") == 12

    con_task.cancel()
