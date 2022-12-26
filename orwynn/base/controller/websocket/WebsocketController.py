from typing import ClassVar

from orwynn.base.controller.Controller import Controller
from orwynn.base.controller.websocket.Websocket import Websocket


class WebsocketController(Controller):
    """Operates on websocket protocol."""
    ROUTE: ClassVar[str | None] = None

    async def process(self, ws: Websocket) -> None:
        pass
