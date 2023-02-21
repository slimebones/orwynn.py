from orwynn.src.boot.Boot import Boot
from orwynn.src.controller.websocket.WebsocketController import WebsocketController
from orwynn.src.module.Module import Module
from orwynn.src.web.websocket.Websocket import Websocket


def test_main_route():
    class WS1(WebsocketController):
        ROUTE = "/hello"

        async def main(self, ws: Websocket) -> None:
            await ws.send_json({"message": "Hello!"})
            await ws.close()

    client = Boot(Module(
        route="/",
        Controllers=[WS1]
    )).app.client

    with client.websocket("/hello") as ws:
        data = ws.receive_json()

    assert data == {"message": "Hello!"}


def test_custom_route():
    class WS1(WebsocketController):
        ROUTE = "/hello"

        async def on_message(self, ws: Websocket) -> None:
            await ws.send_json({"message": "Hello!"})
            await ws.close()

    client = Boot(Module(
        route="/",
        Controllers=[WS1]
    )).app.client

    with client.websocket("/hello/message") as ws:
        data = ws.receive_json()

    assert data == {"message": "Hello!"}


def test_several_routes():
    class WS1(WebsocketController):
        ROUTE = "/hello"

        async def main(self, ws: Websocket) -> None:
            await ws.send_json({"message": "main"})
            await ws.close()

        async def on_message(self, ws: Websocket) -> None:
            await ws.send_json({"message": "message"})
            await ws.close()

        async def on_hello(self, ws: Websocket) -> None:
            await ws.send_json({"message": "hello"})
            await ws.close()

    client = Boot(Module(
        route="/",
        Controllers=[WS1]
    )).app.client

    with client.websocket("/hello") as ws:
        data = ws.receive_json()
        assert data == {"message": "main"}

    with client.websocket("/hello/message") as ws:
        data = ws.receive_json()
        assert data == {"message": "message"}

    with client.websocket("/hello/hello") as ws:
        data = ws.receive_json()
        assert data == {"message": "hello"}
