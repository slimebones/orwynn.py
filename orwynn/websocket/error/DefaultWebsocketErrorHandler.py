from orwynn.base.error.Error import Error
from orwynn.base.exchandler.ExceptionHandler import ExceptionHandler
from orwynn.web.websocket.Websocket import Websocket


class DefaultWebsocketErrorHandler(ExceptionHandler):
    E = Error

    async def handle(self, request: Websocket, error: Error) -> None:
        await request.send_json(error.api)
