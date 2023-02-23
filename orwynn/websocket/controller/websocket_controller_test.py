from orwynn.boot.Boot import Boot
from orwynn.base.controller.websocket.WebsocketController import (
    WebsocketController,
)
from orwynn.base.module.Module import Module
from orwynn.web.websocket.Websocket import Websocket


class ArgumentedCtrl(WebsocketController):
    ROUTE = "/user/{user_id}"

    async def main(
        self,
        ws: Websocket,
        user_id: str,
        order: int | None = None,
        message: str | None = "welcome"
    ) -> None:
        await ws.send_json(dict(
            user_id=user_id,
            message=message,
            order=order
        ))


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


def test_arguments():
    boot: Boot = Boot(
        Module("/", Controllers=[ArgumentedCtrl])
    )

    with boot.client.websocket("/user/eg1?message=hello&order=2") as ws:
        data: dict = ws.receive_json()

        assert data["user_id"] == "eg1"
        assert data["message"] == "hello"
        assert data["order"] == 2


def test_default_query():
    boot: Boot = Boot(
        Module("/", Controllers=[ArgumentedCtrl])
    )

    with boot.client.websocket("/user/eg1") as ws:
        data: dict = ws.receive_json()

        print(data)
        assert data["user_id"] == "eg1"
        assert data["message"] == "welcome"
        assert data["order"] == None
