import pytest

from orwynn.base.module import Module
from orwynn.boot.boot import Boot
from orwynn.di.di import Di
from orwynn.http import HttpMiddleware
from orwynn.utils import validation
from orwynn.websocket import WebsocketMiddleware


@pytest.mark.asyncio
async def test_http():
    """
    Should be able to add custom middleware globally.
    """
    class Mw(HttpMiddleware):
        def __init__(self, covered_routes: list[str]) -> None:
            self.covered_routes_ = covered_routes
            super().__init__(covered_routes)

    await Boot.create(
        Module(),
        global_middleware={
            Mw: ["/hello"]
        }
    )

    mw: Mw = validation.apply(Di.ie().find("Mw"), Mw)
    assert mw.covered_routes_ == ["/hello"]


@pytest.mark.asyncio
async def test_websocket():
    """
    Should be able to add custom middleware globally.
    """
    class Mw(WebsocketMiddleware):
        def __init__(self, covered_routes: list[str]) -> None:
            self.covered_routes_ = covered_routes
            super().__init__(covered_routes)

    await Boot.create(
        Module(),
        global_middleware={
            Mw: ["/hello"]
        }
    )

    mw: Mw = validation.apply(Di.ie().find("Mw"), Mw)
    assert mw.covered_routes_ == ["/hello"]
