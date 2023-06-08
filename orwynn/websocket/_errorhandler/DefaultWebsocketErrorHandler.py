from orwynn.base.errorhandler.errorhandler import ErrorHandler
from orwynn.proxy.BootProxy import BootProxy
from orwynn.websocket._Websocket import Websocket


class DefaultWebsocketErrorHandler(ErrorHandler):
    E = Exception

    async def handle(
        self, request: Websocket, error: Exception
    ) -> None:
        await request.send_json(BootProxy.ie().api_indication.digest(
            error
        ))
