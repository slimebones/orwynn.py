from orwynn.base.middleware import Middleware
from orwynn.websocket.middleware.nextcall import WebsocketNextCall
from orwynn.websocket.websocket import Websocket


class WebsocketMiddleware(Middleware):
    """Intermediate operational layer for Websocket requests.

    Note that websocket methods return None since websocket sends data through
    the Websocket object itself.
    """
    async def dispatch(
        self,
        request: Websocket,
        call_next: WebsocketNextCall
    ) -> None:
        return await super().dispatch(request, call_next)

    async def process(
        self,
        request: Websocket,
        call_next: WebsocketNextCall
    ) -> None:
        return await super().process(request, call_next)
