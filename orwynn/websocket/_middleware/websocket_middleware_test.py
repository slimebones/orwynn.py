from orwynn.base.module.Module import Module
from orwynn.boot._Boot import Boot
from orwynn.testing._Client import Client
from orwynn.websocket import (Websocket, WebsocketController,
                              WebsocketMiddleware, WebsocketNextCall)


class Mw1(WebsocketMiddleware):
    async def process(
        self, request: Websocket, call_next: WebsocketNextCall
    ) -> None:
        await request.send_json({"value": "entry"})
        await call_next(request)


class Ws1(WebsocketController):
    ROUTE = "/"

    async def on_message(self, websocket: Websocket) -> None:
        await websocket.send_json({"value": "hello"})
        await websocket.close()


def test_basic():
    boot: Boot = Boot(Module(
        route="/hello",
        Controllers=[Ws1],
        Middleware=[Mw1]
    ))
    client: Client = boot.app.client

    with client.websocket("/hello/message") as ws:
        data: dict

        data = ws.receive_json()
        assert data == {"value": "entry"}

        data = ws.receive_json()
        assert data == {"value": "hello"}
