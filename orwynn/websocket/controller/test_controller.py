import pytest

from orwynn.apiversion import ApiVersion
from orwynn.base.module.module import Module
from orwynn.boot.boot import Boot
from orwynn.di.di import Di
from orwynn.utils import validation
from orwynn.websocket import Websocket, WebsocketController


class WsCtrl(WebsocketController):
    Route = "/"
    Version = {2, 3}

    async def main(self, ws: Websocket) -> None:
        await ws.send_json({"message": "hello"})

    async def on_connect(self, ws: Websocket) -> None:
        await ws.send_json({"message": "hello"})


class ArgumentedCtrl(WebsocketController):
    Route = "/user/{user_id}"

    async def main(
        self,
        ws: Websocket,
        user_id: str,
        order: int | None = None,
        message: str | None = "welcome"
    ) -> None:
        await ws.send_json({
            "user_id": user_id,
            "message": message,
            "order": order
        })


@pytest.mark.asyncio
async def test_main_route():
    class WS1(WebsocketController):
        Route = "/hello"

        async def main(self, ws: Websocket) -> None:
            await ws.send_json({"message": "Hello!"})
            await ws.close()

    client = (await Boot.create(Module(
        route="/",
        Controllers=[WS1]
    ))).app.client

    with client.websocket("/hello") as ws:
        data = ws.receive_json()

    assert data == {"message": "Hello!"}


@pytest.mark.asyncio
async def test_custom_route():
    class WS1(WebsocketController):
        Route = "/hello"

        async def on_message(self, ws: Websocket) -> None:
            await ws.send_json({"message": "Hello!"})
            await ws.close()

    client = (await Boot.create(Module(
        route="/",
        Controllers=[WS1]
    ))).app.client

    with client.websocket("/hello/message") as ws:
        data = ws.receive_json()

    assert data == {"message": "Hello!"}


@pytest.mark.asyncio
async def test_several_routes():
    class WS1(WebsocketController):
        Route = "/hello"

        async def main(self, ws: Websocket) -> None:
            await ws.send_json({"message": "main"})
            await ws.close()

        async def on_message(self, ws: Websocket) -> None:
            await ws.send_json({"message": "message"})
            await ws.close()

        async def on_hello(self, ws: Websocket) -> None:
            await ws.send_json({"message": "hello"})
            await ws.close()

    client = (await Boot.create(Module(
        route="/",
        Controllers=[WS1]
    ))).app.client

    with client.websocket("/hello") as ws:
        data = ws.receive_json()
        assert data == {"message": "main"}

    with client.websocket("/hello/message") as ws:
        data = ws.receive_json()
        assert data == {"message": "message"}

    with client.websocket("/hello/hello") as ws:
        data = ws.receive_json()
        assert data == {"message": "hello"}


@pytest.mark.asyncio
async def test_arguments():
    boot: Boot = await Boot.create(
        Module("/", Controllers=[ArgumentedCtrl])
    )

    with boot.client.websocket("/user/eg1?message=hello&order=2") as ws:
        data: dict = ws.receive_json()

        assert data["user_id"] == "eg1"
        assert data["message"] == "hello"
        assert data["order"] == 2


@pytest.mark.asyncio
async def test_default_query():
    boot: Boot = await Boot.create(
        Module("/", Controllers=[ArgumentedCtrl])
    )

    with boot.client.websocket("/user/eg1") as ws:
        data: dict = ws.receive_json()

        assert data["user_id"] == "eg1"
        assert data["message"] == "welcome"
        assert data["order"] is None



@pytest.mark.asyncio
async def test_final_routes():
    await Boot.create(
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
