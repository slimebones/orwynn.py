from orwynn import web
from orwynn.boot.Boot import Boot
from orwynn.controller.websocket.WebsocketController import WebsocketController
from orwynn.middleware.WebsocketMiddleware import WebsocketMiddleware
from orwynn.middleware.WebsocketNextCallFn import WebsocketNextCallFn
from orwynn.module.Module import Module
from orwynn.testing.Client import Client


class Mw1(WebsocketMiddleware):
    async def process(
        self, request: web.Websocket, call_next: WebsocketNextCallFn
    ) -> None:
        await request.send_json({"value": "entry"})
        await call_next(request)


class Ws1(WebsocketController):
    ROUTE = "/"

    async def on_message(self, websocket: web.Websocket) -> None:
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
