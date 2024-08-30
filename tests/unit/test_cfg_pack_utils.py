import pytest

from orwynn._cfg import Cfg, CfgPackUtils


class _Cfg1(Cfg):
    num: int

class _Cfg2(Cfg):
    num: int

class _Cfg3(Cfg):
    num: int

class _Cfg4(Cfg):
    num: int

@pytest.mark.asyncio
async def test_bake():
    f = await CfgPackUtils.bake_cfgs(
        "prod-very-local",
        {
            "__default__": [
                _Cfg1(num=0),
                _Cfg2(num=0),
                _Cfg3(num=0)
            ],
            "test": [
                _Cfg1(num=1),
                _Cfg2(num=1)
            ],
            "dev": [
                _Cfg1(num=2),
                _Cfg2(num=2)
            ],
            "prod": [
                _Cfg1(num=3),
                _Cfg2(num=3)
            ],
            "prod->prod-local": [
                _Cfg1(num=4),
                _Cfg2(num=4),
                _Cfg3(num=4)
            ],
            "prod-local->prod-very-local": [
                _Cfg3(num=5),
                _Cfg4(num=5)
            ]
        }
    )

    assert sorted(f, key=lambda cfg: cfg.__class__.__name__) == [
        _Cfg1(num=4),
        _Cfg2(num=4),
        _Cfg3(num=5),
        _Cfg4(num=5)
    ]

