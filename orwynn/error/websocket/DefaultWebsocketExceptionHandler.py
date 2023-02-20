from orwynn import web
from orwynn.error.ExceptionHandler import ExceptionHandler
from orwynn.proxy.BootProxy import BootProxy


class DefaultWebsocketExceptionHandler(ExceptionHandler):
    E = Exception

    async def handle(
        self, request: web.Websocket, error: Exception
    ) -> None:
        await request.send_json(BootProxy.ie().api_indication.digest(
            error
        ))
