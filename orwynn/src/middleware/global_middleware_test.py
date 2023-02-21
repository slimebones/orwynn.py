from orwynn import validation
from orwynn.src.boot.Boot import Boot
from orwynn.src.di.Di import Di
from orwynn.src.middleware.HttpMiddleware import HttpMiddleware
from orwynn.src.middleware.WebsocketMiddleware import WebsocketMiddleware
from orwynn.src.module.Module import Module


def test_http():
    """
    Should be able to add custom middleware globally.
    """
    class Mw(HttpMiddleware):
        def __init__(self, covered_routes: list[str]) -> None:
            self.covered_routes_ = covered_routes
            super().__init__(covered_routes)

    Boot(
        Module(),
        global_middleware={
            Mw: ["/hello"]
        }
    )

    mw: Mw = validation.apply(Di.ie().find("Mw"), Mw)
    assert mw.covered_routes_ == ["/hello"]


def test_websocket():
    """
    Should be able to add custom middleware globally.
    """
    class Mw(WebsocketMiddleware):
        def __init__(self, covered_routes: list[str]) -> None:
            self.covered_routes_ = covered_routes
            super().__init__(covered_routes)

    Boot(
        Module(),
        global_middleware={
            Mw: ["/hello"]
        }
    )

    mw: Mw = validation.apply(Di.ie().find("Mw"), Mw)
    assert mw.covered_routes_ == ["/hello"]
