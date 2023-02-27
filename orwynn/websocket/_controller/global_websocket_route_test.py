import starlette.websockets

from orwynn.apiversion import ApiVersion
from orwynn.boot._Boot import Boot
from .WebsocketController import (
    WebsocketController
)
from orwynn.base.module._Module import Module
from orwynn.websocket import Websocket


class WsCtrl(WebsocketController):
    ROUTE = "/message"

    async def main(self, ws: Websocket) -> None:
        await ws.send_json({"message": "hello"})


def test_default():
    """
    By default a client should use the global route.
    """
    boot: Boot = Boot(
        root_module=Module("/", Controllers=[WsCtrl]),
        global_websocket_route="/donuts"
    )

    with boot.app.client.websocket("/message") as ws:
        data: dict = ws.receive_json()
        assert data["message"] == "hello"


def test_default_version():
    """
    By default a client should use the latest api version available.
    """
    class _C(WsCtrl):
        VERSION = 3

        async def main(self, ws: Websocket) -> None:
            return await super().main(ws)

    boot: Boot = Boot(
        root_module=Module("/", Controllers=[_C]),
        global_websocket_route="/ws/v{version}",
        api_version=ApiVersion(
            supported={1, 2, 3}
        )
    )

    with boot.app.client.websocket("/message") as ws:
        data: dict = ws.receive_json()
        assert data["message"] == "hello"


def test_not_used():
    """
    The global route can be disabled.
    """
    boot: Boot = Boot(
        root_module=Module("/", Controllers=[WsCtrl]),
        global_websocket_route="/donuts"
    )

    with boot.app.client.websocket(
        "/donuts/message",
        is_global_route_used=False
    ) as ws:
        data: dict = ws.receive_json()
        assert data["message"] == "hello"


def test_pass_version():
    """
    A client is able to not specify global route, but pass own api version.
    """
    class _C(WsCtrl):
        VERSION = 2

        async def main(self, ws: Websocket) -> None:
            return await super().main(ws)

    boot: Boot = Boot(
        root_module=Module("/", Controllers=[_C]),
        global_websocket_route="/ws/v{version}",
        api_version=ApiVersion(
            supported={1, 2, 3}
        )
    )

    try:
        with boot.app.client.websocket(
            "/message",
            api_version=1
        ) as ws:
            pass
    except starlette.websockets.WebSocketDisconnect:
        pass
    else:
        raise AssertionError()

    with boot.app.client.websocket(
        "/message",
        api_version=2
    ) as ws:
        data: dict = ws.receive_json()
        assert data["message"] == "hello"

    try:
        with boot.app.client.websocket(
            "/message",
            api_version=3
        ) as ws:
            pass
    except starlette.websockets.WebSocketDisconnect:
        pass
    else:
        raise AssertionError()
