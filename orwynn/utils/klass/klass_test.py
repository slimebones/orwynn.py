import pytest

from orwynn.utils.klass import bind_first_arg, bind_first_arg_async


def test_bind_first_arg():
    class A:
        def hello(self, x: str, y: int) -> str:
            return x * y

    a = A()
    assert bind_first_arg(a)(A.hello)("wow", 4) == "wowwowwowwow"


@pytest.mark.asyncio
async def test_bind_first_arg_async():
    class A:
        async def hello(self, x: str, y: int) -> str:
            return x * y

    a = A()
    assert await bind_first_arg_async(a)(A.hello)("wow", 4) == "wowwowwowwow"
