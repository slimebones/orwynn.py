from orwynn.boot.api_version.ApiVersion import ApiVersion
from orwynn.boot.Boot import Boot
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.controller.http.HttpController import HttpController
from orwynn.controller.websocket.WebsocketController import WebsocketController
from orwynn.module.Module import Module
from orwynn.web.websocket.Websocket import Websocket


class C(WebsocketController):
    ROUTE = "/message"

    async def main(self, ws: Websocket) -> None:
        await ws.send_json({"message": "hello"})


def test_default():
    """
    By default a client should use the global route.
    """
    boot: Boot = Boot(
        root_module=Module("/", Controllers=[C]),
        global_websocket_route="/donuts"
    )

    boot.app.client.websocket("/message")


def test_default_version():
    """
    By default a client should use the latest api version available.
    """
    class _C(C):
        ROUTE = "/"
        VERSION = 3

        async def main(self, ws: Websocket) -> None:
            await ws.send_json({})

    boot: Boot = Boot(
        root_module=Module("/", Controllers=[_C]),
        global_websocket_route="/ws/v{version}",
        api_version=ApiVersion(
            supported={1, 2, 3}
        )
    )

    boot.app.client.websocket("/message")


def test_not_used():
    """
    The global route can be disabled.
    """
    boot: Boot = Boot(
        root_module=Module("/", Controllers=[C]),
        global_websocket_route="/donuts"
    )

    boot.app.client.websocket(
        "/donuts/message",
        is_global_route_used=False
    )


def test_pass_version():
    """
    A client is able to not specify global route, but pass own api version.
    """
    class _C(C):
        ROUTE = "/message"
        ENDPOINTS = [Endpoint(method="get")]
        VERSION = 2

        def get(self) -> dict:
            return {"message": "hello"}

    boot: Boot = Boot(
        root_module=Module("/user", Controllers=[_C]),
        global_websocket_route="/ws/v{version}",
        api_version=ApiVersion(
            supported={1, 2, 3}
        )
    )

    boot.app.client.websocket(
        "/message",
        api_version=1
    )
    boot.app.client.websocket(
        "/message",
        api_version=2
    )
    boot.app.client.websocket(
        "/message",
        api_version=3
    )
