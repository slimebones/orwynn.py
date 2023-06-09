from orwynn.base.module.module import Module
from orwynn.boot.boot import Boot
from orwynn.context.errors import UndefinedStorageError
from orwynn.utils import validation
from orwynn.websocket._context.id import (
    WebsocketRequestContextId,
)
from orwynn.websocket._controller.controller import (
    WebsocketController,
)
from orwynn.websocket._log.middleware import LogWebsocketMiddleware
from orwynn.websocket.websocket import Websocket


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
    )  # type: ignore @worker

    validation.expect(
        WebsocketRequestContextId().get,
        UndefinedStorageError
    )

    with boot.app.client.websocket("/") as ws:
        data: dict = ws.receive_json()
        assert type(data["request_id"]) is str and data["request_id"] != ""
