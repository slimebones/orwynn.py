from orwynn.src.middleware.Middleware import Middleware
from orwynn.src.middleware.WebsocketNextCall import WebsocketNextCall
from orwynn.src.web.websocket.Websocket import Websocket


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
