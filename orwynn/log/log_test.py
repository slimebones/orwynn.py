import json
from pprint import pprint

import pytest

from orwynn import validation
from orwynn.boot.Boot import Boot
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.controller.http.HTTPController import HTTPController
from orwynn.di.DI import DI
from orwynn.log.Log import Log
from orwynn.module.Module import Module
from orwynn.testing import get_log_apprc
from orwynn.web.context.RequestContextId import RequestContextId


def test_logged_request_id():
    class C1(HTTPController):
        ROUTE = "/"
        ENDPOINTS = [
            Endpoint(method="get")
        ]

        def get(self) -> dict:
            Log.info("hello")
            return {}

    def __check(message) -> None:
        data: dict = json.loads(str(message))
        extra: dict = data["record"]["extra"]

        pprint(data)

        assert isinstance(extra["request_id"], str)

    boot: Boot = Boot(
        Module("/", Controllers=[C1]),
        apprc=get_log_apprc(__check)
    )

    boot.app.client.get("/", 200)
    assert 0
