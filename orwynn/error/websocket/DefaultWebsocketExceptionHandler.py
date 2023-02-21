from orwynn.error.ExceptionHandler import ExceptionHandler
from orwynn.proxy.BootProxy import BootProxy
from orwynn.web.websocket.Websocket import Websocket


class DefaultWebsocketExceptionHandler(ExceptionHandler):
    E = Exception

    async def handle(
        self, request: Websocket, error: Exception
    ) -> None:
        await request.send_json(BootProxy.ie().api_indication.digest(
            error
        ))
