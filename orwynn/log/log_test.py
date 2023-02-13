import json

import pytest

from orwynn import validation
from orwynn.boot.Boot import Boot
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.controller.http.HTTPController import HTTPController
from orwynn.di.DI import DI
from orwynn.log import module as log_module
from orwynn.log.Log import Log
from orwynn.module.Module import Module
from orwynn.testing import get_log_apprc


@pytest.fixture
def log() -> Log:
    return validation.apply(DI.ie().find("Log"), Log)


def test_logged_request_id():
    class C1(HTTPController):
        ROUTE = "/"
        ENDPOINTS = [
            Endpoint(method="get")
        ]

        def __init__(self, log: Log) -> None:
            super().__init__()
            self.__log: Log = log

        def get(self) -> dict:
            self.__log.info("hello")
            return {}

    def __check(message) -> None:
        data: dict = json.loads(str(message))
        extra: dict = data["record"]["extra"]

        assert 0

        assert isinstance(extra["request_id"], str)

    boot: Boot = Boot(
        Module("/", Controllers=[C1], imports=[log_module]),
        apprc=get_log_apprc(__check)
    )

    boot.app.client.get("/", 200)
