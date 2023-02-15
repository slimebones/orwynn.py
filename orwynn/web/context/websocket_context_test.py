from orwynn import validation, web
from orwynn.boot.Boot import Boot
from orwynn.controller.websocket.WebsocketController import WebsocketController
from orwynn.log.LogWebsocketMiddleware import LogWebsocketMiddleware
from orwynn.module.Module import Module
from orwynn.web.context.UndefinedStorageError import UndefinedStorageError
from orwynn.web.context.WebsocketRequestContextId import (
    WebsocketRequestContextId,
)


def test_basic():
    """Request id should be fetchable from context within request-response
    cycle and unfetchable outside this cycle.
    """
    class C1(WebsocketController):
        ROUTE = "/"

        async def main(self, websocket: web.Websocket) -> None:
            await websocket.send_json(
                {"request_id": WebsocketRequestContextId().get()}
            )

    boot: Boot = Boot(
        Module(
            "/",
            Controllers=[C1],
            Middleware=[LogWebsocketMiddleware]
        )
    )

    validation.expect(
        WebsocketRequestContextId().get,
        UndefinedStorageError
    )

    with boot.app.client.websocket("/") as ws:
        data: dict = ws.receive_json()
        assert type(data["request_id"]) is str and data["request_id"] != ""
