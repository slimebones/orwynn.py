import pytest

from orwynn.base.module.module import Module
from orwynn.boot.boot import Boot
from orwynn.testing.client import Client
from orwynn.websocket import (
    Websocket,
    WebsocketController,
    WebsocketMiddleware,
    WebsocketNextCall,
)


class Mw1(WebsocketMiddleware):
    async def process(
        self, request: Websocket, call_next: WebsocketNextCall
    ) -> None:
        await request.send_json({"value": "entry"})
        await call_next(request)


class Ws1(WebsocketController):
    Route = "/"

    async def on_message(self, websocket: Websocket) -> None:
        await websocket.send_json({"value": "hello"})
        await websocket.close()


@pytest.mark.asyncio
async def test_basic():
    boot: Boot = await Boot.create(Module(
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
