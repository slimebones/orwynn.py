from typing import ClassVar

from orwynn.controller.Controller import Controller
from orwynn.controller.websocket.Websocket import Websocket


class WebsocketController(Controller):
    """Operates on websocket protocol."""
    ROUTE: ClassVar[str | None] = None

    async def process(self, ws: Websocket) -> None:
        pass
