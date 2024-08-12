from orwynn import _merge
from orwynn._pepel import AsyncPipeline
from ryz.res import Res

def test_merge():
    async def f1(inp) -> Res: ...
    async def f2(inp) -> Res: ...
    async def f3(inp) -> Res: ...

    d1 = {
        "pipeline": AsyncPipeline(f1, f2),
        "nested": {
            "pipeline": AsyncPipeline(f3)
        }
    }
    d2 = {
        "pipeline": AsyncPipeline(f3),
        "nested": {
            "pipeline": AsyncPipeline(f2, f1)
        }
    }

    d3 = _merge(d1, d2).eject()
    pipeline: AsyncPipeline = d3["pipeline"]
    assert list(pipeline) == [f1, f2, f3]
    nested_pipeline: AsyncPipeline = d3["nested"]["pipeline"]
    assert list(nested_pipeline) == [f3, f2, f1]
