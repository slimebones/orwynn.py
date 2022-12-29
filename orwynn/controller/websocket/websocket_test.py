from orwynn.boot.Boot import Boot
from orwynn.controller.websocket.Websocket import Websocket
from orwynn.controller.websocket.WebsocketController import WebsocketController
from orwynn.model.Model import Model
from orwynn.module.Module import Module


def test_basic():
    class Ws1(WebsocketController):
        ROUTE = "/hello"

        async def process(self, ws: Websocket) -> None:
            await ws.accept()
            await ws.send_json({"message": "Hello!"})
            await ws.close()

    client = Boot(Module(
        route="/",
        Controllers=[Ws1]
    )).app.client

    with client.ws("/hello") as ws:
        data = ws.receive_json()

    assert data == {"message": "Hello!"}
