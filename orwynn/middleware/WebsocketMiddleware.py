from orwynn import web
from orwynn.middleware.Middleware import Middleware
from orwynn.middleware.WebsocketNextCall import WebsocketNextCall


class WebsocketMiddleware(Middleware):
    """Intermediate operational layer for Websocket requests.

    Note that websocket methods return None since websocket sends data through
    the Websocket object itself.
    """
    async def dispatch(
        self,
        request: web.Websocket,
        call_next: WebsocketNextCall
    ) -> None:
        return await super().dispatch(request, call_next)

    async def process(
        self,
        request: web.Websocket,
        call_next: WebsocketNextCall
    ) -> None:
        return await super().process(request, call_next)