from orwynn.src import validation
from orwynn.src.boot.Boot import Boot
from orwynn.src.controller.websocket.WebsocketController import (
    WebsocketController,
)
from orwynn.src.log.LogWebsocketMiddleware import LogWebsocketMiddleware
from orwynn.src.module.Module import Module
from orwynn.src.web.context.UndefinedStorageError import UndefinedStorageError
from orwynn.src.web.context.WebsocketRequestContextId import (
    WebsocketRequestContextId,
)
from orwynn.src.web.websocket.Websocket import Websocket


def test_basic():
    """Request id should be fetchable from context within request-response
    cycle and unfetchable outside this cycle.
    """
    class C1(WebsocketController):
        ROUTE = "/"

        async def main(self, websocket: Websocket) -> None:
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
