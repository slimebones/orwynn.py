import asyncio

from ryz.core import Code
from ryz.core import Ok, Res
from ryz.uuid import uuid4
from orwynn.yon.server import Bus, PubOpts, RpcSend, ok

from orwynn import (
    App,
    AppCfg,
    GlobalSysOpts,
    Plugin,
    RsysSpec,
    SysInp,
    SysOpts,
    SysSpec,
)
from orwynn._pepel import AsyncPipeline
from tests.conftest import Mock_1, MockCfg, MockCon


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
        Mock_1(key="hello"), PubOpts(pubr_timeout=1))).unwrap()
    assert isinstance(r, ok)

async def test_pipeline(app_cfg: AppCfg):
    async def add_str(inp: SysInp[Mock_1, MockCfg]) -> Res[SysInp]:
        inp.msg.key += "h"
        if "usages" not in inp.extra:
            inp.extra["usages"] = 0
        inp.extra["usages"] += 1
        assert inp.extra["usages"] == inp.msg.key.count("h")
        return Ok(inp)

    async def rpc_mock(inp: SysInp[Mock_1, MockCfg]) -> Res[SysInp]:
        assert inp.msg.key.startswith("start-")
        assert inp.msg.key.count("h") == 8
        assert inp.extra["usages"] == 8
        return inp.ok(inp.msg)

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
                pipeline_after=AsyncPipeline(add_str, add_str)
            ),
            sys=SysOpts(
                pipeline_before=AsyncPipeline(add_str, add_str),
                pipeline_after=AsyncPipeline(add_str, add_str)
            ),
            rsys=SysOpts(
                pipeline_before=AsyncPipeline(add_str, add_str),
                pipeline_after=AsyncPipeline(add_str, add_str)
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
    con_task = asyncio.create_task(app.get_bus().unwrap().con(con))
    await con.client_recv()
    await con.client_send({
        "sid": uuid4(),
        "codeid": (await Code.get_regd_codeid_by_type(RpcSend)).unwrap(),
        "msg": {
            "key": "test::mock",
            "data": {
                "key": "start-"
            }
        }
    })
    out = Mock_1.model_validate((await con.client_recv())["msg"])
    assert out.key.startswith("start-")
    assert out.key.count("h") == 16

    con_task.cancel()
