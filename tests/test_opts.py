from orwynn import _merge
from orwynn._pepel import AsyncPipeline
from ryz.res import Res

def test_merge():
    async def f1(inp) -> Res: ...
    async def f2(inp) -> Res: ...
    async def f3(inp) -> Res: ...

    d1 = {
        "pipeline": AsyncPipeline(f1, f2)
    }
    d2 = {
        "pipeline": AsyncPipeline(f3)
    }

    d3 = _merge(d1, d2).eject()
