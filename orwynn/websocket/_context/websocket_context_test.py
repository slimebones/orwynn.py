from orwynn.base.module._Module import Module
from orwynn.boot._Boot import Boot
from orwynn.context.errors import UndefinedStorageError
from orwynn.utils import validation
from orwynn.websocket._context.WebsocketRequestContextId import (
    WebsocketRequestContextId,
)
from orwynn.websocket._controller.WebsocketController import (
    WebsocketController,
)
from orwynn.websocket._log.LogWebsocketMiddleware import LogWebsocketMiddleware
from orwynn.websocket._Websocket import Websocket


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
