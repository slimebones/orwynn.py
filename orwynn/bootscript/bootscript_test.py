from orwynn._di.Di import Di
from orwynn.boot import Boot
from orwynn.base.module import Module
from orwynn.base.service import Service
from orwynn.bootscript._Bootscript import Bootscript
from orwynn.bootscript._CallTime import CallTime
from orwynn.util import validation


class SomeService(Service):
    def __init__(self) -> None:
        super().__init__()
        self.some_var: int = 0


def some_bootscript(some_service: SomeService) -> None:
    some_service.some_var = 1


def test_basic():
    boot: Boot = Boot(
        Module(),
        bootscripts=[
            Bootscript(
                fn=some_bootscript,
                call_time=CallTime.AFTER_ALL
            )
        ]
    )

    some_service: SomeService = validation.apply(
        Di.ie().find("SomeService"),
        SomeService
    )

    assert some_service.some_var == 1
