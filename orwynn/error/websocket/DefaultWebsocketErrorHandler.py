from orwynn import web
from orwynn.error.Error import Error
from orwynn.error.ExceptionHandler import ExceptionHandler


class DefaultWebsocketErrorHandler(ExceptionHandler):
    E = Error

    async def handle(self, request: web.Websocket, error: Error) -> None:
        await request.send_json(error.api)
