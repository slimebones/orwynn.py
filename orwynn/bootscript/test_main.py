import pytest

from orwynn.base.module import Module
from orwynn.base.service import Service
from orwynn.boot import Boot
from orwynn.bootscript.bootscript import Bootscript
from orwynn.bootscript.calltime import CallTime
from orwynn.di.di import Di
from orwynn.utils import validation


class SomeService(Service):
    def __init__(self) -> None:
        super().__init__()
        self.some_var: int = 0


def fn(some_service: SomeService) -> None:
    some_service.some_var = 1


async def async_fn(some_service: SomeService) -> None:
    some_service.some_var = 5


@pytest.mark.asyncio
async def test_basic():
    await Boot.create(
        Module(Providers=[SomeService]),
        bootscripts=[
            Bootscript(
                fn=fn,
                call_time=CallTime.AFTER_ALL
            )
        ]
    )

    some_service: SomeService = validation.apply(
        Di.ie().find("SomeService"),
        SomeService
    )

    assert some_service.some_var == 1


@pytest.mark.asyncio
async def test_async():
    await Boot.create(
        Module(Providers=[SomeService]),
        bootscripts=[
            Bootscript(
                fn=fn,
                call_time=CallTime.AFTER_ALL
            )
        ]
    )

    some_service: SomeService = validation.apply(
        Di.ie().find("SomeService"),
        SomeService
    )

    assert some_service.some_var == 1
