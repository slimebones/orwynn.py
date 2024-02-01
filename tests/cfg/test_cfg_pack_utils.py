from pykit.tree import TreeUtils
import pytest

from orwynn.cfg import Cfg, CfgPackUtils

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
    f = await CfgPackUtils._bake_cfg_pack_reversed_tree(
        {
            "__default__": [
                _Cfg1(num=0),
                _Cfg2(num=0),
                _Cfg3(num=0),
                _Cfg4(num=0)
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
            ]
        }
    )

    for x in f:
        print(x)

    assert 0

