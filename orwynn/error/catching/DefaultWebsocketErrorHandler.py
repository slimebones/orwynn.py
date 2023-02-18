from orwynn import web
from orwynn.error.catching.ExceptionHandler import ExceptionHandler
from orwynn.error.Error import Error
from orwynn.web import JsonResponse, Request, Response


class DefaultWebsocketErrorHandler(ExceptionHandler):
    E = Error

    async def handle(self, request: web.Websocket, error: Error) -> None:
        await request.send_json(error.api)
