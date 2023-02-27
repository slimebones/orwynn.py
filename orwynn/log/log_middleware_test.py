import json
from types import NoneType
from typing import Literal

from orwynn.boot._Boot import Boot
from orwynn.base.error import Error
from orwynn.log._Log import Log
from orwynn.http import LogMiddleware, Endpoint, HttpController
from orwynn.base.module._Module import Module
from orwynn.testing import Writer
from orwynn.testing._Client import Client


def __check_log_message(message: str) -> list[dict]:
    assert message != ""
    items: list[str] = message.split("\n")
    parsed_items: list[dict] = []

    for item in items:
        if item == "":
            continue
        data: dict = json.loads(str(item))
        extra: dict = data["record"]["extra"]

        request_or_response: Literal["http.request", "http.response"]
        if "http.request" in extra and "http.response" not in extra:
            request_or_response = "http.request"
            request_data: dict = extra["http.request"]
            assert type(request_data["id"]) is str
            assert type(request_data["url"]) is str
        elif "http.response" in extra and "http.request" not in extra:
            request_or_response = "http.response"
            response_data: dict = extra["http.response"]
            assert type(response_data["request_id"]) is str
            assert type(response_data["status_code"]) is int
            assert type(response_data["media_type"]) in [str, NoneType]
        else:
            raise AssertionError()

        assert type(extra[request_or_response]["headers"]) is dict
        assert extra[request_or_response]["json"] is None or (
            # Empty json dict is not allowed in log extra - it should be
            # replaced with None.
            type(extra[request_or_response]["json"]) is dict
            and extra[request_or_response]["json"] != {}
        )

        parsed_items.append(data)

    return parsed_items


def test_get(
    writer: Writer,
    log_apprc_sink_to_writer: dict
):
    RETURNED_DATA: dict = {"hello": 1}

    class C1(HttpController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self) -> dict:
            return RETURNED_DATA

    boot: Boot = Boot(
        Module(
            route="/", Controllers=[C1], Middleware=[LogMiddleware]
        ),
        apprc=log_apprc_sink_to_writer
    )
    client: Client = boot.app.client
    client.get(
        "/",
        200
    )

    items: list[dict] = __check_log_message(writer.read())
    for item in items:
        extra: dict = item["record"]["extra"]
        if "request" in extra:
            assert extra["http.request"]["json"] is None
        elif "response" in extra:
            assert extra["http.response"]["json"] == RETURNED_DATA

    Log.remove()


def test_get__error(
    writer: Writer,
    log_apprc_sink_to_writer: dict
):
    class C1(HttpController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self) -> dict:
            raise Error("hello")

    boot: Boot = Boot(
        Module(
            route="/", Controllers=[C1], Middleware=[LogMiddleware]
        ),
        apprc=log_apprc_sink_to_writer
    )
    client: Client = boot.app.client
    client.get(
        "/",
        400
    )

    items: list[dict] = __check_log_message(writer.read())
    for item in items:
        extra: dict = item["record"]["extra"]
        if "request" in extra:
            assert extra["http.request"]["json"] is None
        elif "response" in extra:
            assert extra["http.response"]["json"] == Error("hello").api

    Log.remove()
