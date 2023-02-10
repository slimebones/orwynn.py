import json
from typing import Callable

from loguru._handler import Message

from orwynn.boot.Boot import Boot
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.controller.http.HTTPController import HTTPController
from orwynn.error.Error import Error
from orwynn.error.MalfunctionError import MalfunctionError
from orwynn.module.Module import Module
from orwynn.test.Client import Client


def __get_log_apprc(check_fn: Callable) -> dict:
    return {
        "prod": {
            "Log": {
                "handlers": [
                    {
                        "sink": check_fn,
                        "serialize": True
                    }
                ]
            }
        }
    }


def __check_log_message(message: Message) -> dict:
    data: dict = json.loads(str(message))
    extra: dict = data["record"]["extra"]

    assert extra["type"] in ["request", "response"]
    assert type(extra["headers"]) is dict
    assert extra["json"] is None or (
        # Empty json dict is not allowed in log extra - it should be replaced
        # with None.
        type(extra["json"]) is dict and extra["json"] != {}
    )

    if extra["type"] == "request":
        assert type(extra["id"]) is str
        assert type(extra["url"]) is str
    elif extra["type"] == "response":
        assert type(extra["request_id"]) is str
        assert type(extra["status_code"]) is int
        assert type(extra["media_type"]) is str
    else:
        raise MalfunctionError

    return data


def test_get():
    RETURNED_DATA: dict = {"hello": 1}

    class C1(HTTPController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self) -> dict:
            return RETURNED_DATA

    def __check(message: Message) -> None:
        data: dict = __check_log_message(message)
        json: dict | None = data["extra"]["json"]

        if data["record"]["extra"]["type"] == "request":
            assert json is None
        elif data["record"]["extra"]["type"] == "response":
            assert json == RETURNED_DATA

    client: Client = Boot(
        Module(route="/", Controllers=[C1]),
        apprc=__get_log_apprc(__check)
    ).app.client

    client.get(
        "/",
        200
    )


def test_get__error():
    class C1(HTTPController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self) -> dict:
            raise Error("hello")

    def __check(message: Message) -> None:
        data: dict = __check_log_message(message)
        json: dict | None = data["extra"]["json"]

        if data["extra"]["type"] == "request":
            assert json is None
        elif data["extra"]["type"] == "response":
            assert json == Error("hello").api

    client: Client = Boot(
        Module(route="/", Controllers=[C1]),
        apprc=__get_log_apprc(__check)
    ).app.client

    client.get(
        "/",
        400
    )
