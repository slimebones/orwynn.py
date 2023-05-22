import json

import pytest
from loguru._handler import Message

from orwynn.base.module._Module import Module
from orwynn.boot._Boot import Boot
from orwynn.http import Endpoint, HttpController
from orwynn.log._Log import Log
from orwynn.testing import Writer, get_log_apprc
from orwynn.websocket import Websocket, WebsocketController


@pytest.fixture
def writer() -> Writer:
    return Writer()


@pytest.fixture
def log_apprc_sink_to_writer(writer: Writer) -> dict:
    def __check(message: Message):
        writer.write(message)
    return get_log_apprc(__check)


def test_logged_request_id(writer: Writer, log_apprc_sink_to_writer: dict):
    class C1(HttpController):
        ROUTE = "/"
        ENDPOINTS = [
            Endpoint(method="get")
        ]

        def get(self) -> dict:
            Log.info("hello")
            return {}

    boot: Boot = Boot(
        Module("/", Controllers=[C1]),
        apprc=log_apprc_sink_to_writer
    )  # type: ignore #worker

    boot.app.client.get("/", 200)
    data: dict = json.loads(str(writer.read()))
    extra: dict = data["record"]["extra"]

    assert isinstance(extra["http.request_id"], str)


def test_logged_websocket_request_id(
    writer: Writer,
    log_apprc_sink_to_writer: dict
):
    class C1(WebsocketController):
        ROUTE = "/"

        async def main(self, websocket: Websocket) -> None:
            Log.info("hello")

    boot: Boot = Boot(
        Module("/", Controllers=[C1]),
        apprc=log_apprc_sink_to_writer
    )  # type: ignore #worker

    with boot.app.client.websocket("/"):
        pass

    raw: str = str(writer.read())
    assert raw != ""

    data: dict = json.loads(raw)
    extra: dict = data["record"]["extra"]
    assert isinstance(extra["websocket.request_id"], str)
