from orwynn._di.Di import Di
from orwynn.apiversion import ApiVersion
from orwynn.base import Module
from orwynn.boot import Boot
from orwynn.utils import validation
from orwynn.websocket import Websocket, WebsocketController


class WsCtrl(WebsocketController):
    ROUTE = "/"
    VERSION = {2, 3}

    async def main(self, ws: Websocket) -> None:
        await ws.send_json({"message": "hello"})

    async def on_connect(self, ws: Websocket) -> None:
        await ws.send_json({"message": "hello"})


def test_final_routes():
    Boot(
        Module(
            "/",
            Controllers=[WsCtrl]
        ),
        api_version=ApiVersion(supported={1, 2, 3}),
        global_websocket_route="/ws/v{version}"
    )

    wsctrl: WsCtrl = validation.apply(Di.ie().find("WsCtrl"), WsCtrl)

    assert wsctrl.final_routes == {
        "/ws/v2", "/ws/v3", "/ws/v2/connect", "/ws/v3/connect"
    }
