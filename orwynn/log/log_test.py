import json
from pprint import pprint
import time
from typing import Optional

import pytest
from loguru._handler import Message

from orwynn import validation
from orwynn.boot.Boot import Boot
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.controller.http.HTTPController import HTTPController
from orwynn.di.DI import DI
from orwynn.log.Log import Log
from orwynn.log.LogMiddleware import LogMiddleware
from orwynn.module.Module import Module
from orwynn.testing import Writer, get_log_apprc
from orwynn.web.context.RequestContextId import RequestContextId


@pytest.fixture
def writer() -> Writer:
    return Writer()


@pytest.fixture
def log_apprc_sink_to_writer(writer: Writer) -> dict:
    def __check(message: Message):
        writer.write(message)
    return get_log_apprc(__check)


def test_logged_request_id(writer: Writer, log_apprc_sink_to_writer: dict):
    class C1(HTTPController):
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
    )

    boot.app.client.get("/", 200)
    data: dict = json.loads(str(writer.read()))
    extra: dict = data["record"]["extra"]

    assert isinstance(extra["request_id"], str)
