from orwynn.src.error.Error import Error
from orwynn.src.error.ExceptionHandler import ExceptionHandler
from orwynn.src.web.websocket.Websocket import Websocket


class DefaultWebsocketErrorHandler(ExceptionHandler):
    E = Error

    async def handle(self, request: Websocket, error: Error) -> None:
        await request.send_json(error.api)
