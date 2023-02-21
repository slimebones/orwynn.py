import json

from orwynn.src.boot.Boot import Boot
from orwynn.src.controller.websocket.WebsocketController import (
    WebsocketController,
)
from orwynn.src.log.Log import Log
from orwynn.src.log.LogWebsocketMiddleware import LogWebsocketMiddleware
from orwynn.src.module.Module import Module
from orwynn.src.testing import Writer
from orwynn.src.testing.Client import Client
from orwynn.src.web.websocket.Websocket import Websocket


def test_get(
    writer: Writer,
    log_apprc_sink_to_writer: dict
):
    class C1(WebsocketController):
        ROUTE = "/"

        async def main(self, websocket: Websocket) -> None:
            await websocket.close()

    boot: Boot = Boot(
        Module(
            route="/", Controllers=[C1], Middleware=[LogWebsocketMiddleware]
        ),
        apprc=log_apprc_sink_to_writer
    )
    client: Client = boot.app.client

    with client.websocket("/"):
        pass

    __check_log_message(writer.read())
    Log.remove()


def __check_log_message(message: str) -> list[dict]:
    assert message != ""
    items: list[str] = message.split("\n")
    parsed_items: list[dict] = []

    for item in items:
        if item == "":
            continue
        data: dict = json.loads(str(item))
        extra: dict = data["record"]["extra"]

        request_data: dict = extra["websocket.request"]
        assert type(request_data["id"]) is str
        assert type(request_data["url"]) is str
        assert type(request_data["headers"]) is dict

        parsed_items.append(data)

    return parsed_items
