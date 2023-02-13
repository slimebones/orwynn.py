import json
from typing import Literal

from orwynn.boot.Boot import Boot
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.controller.http.HTTPController import HTTPController
from orwynn.error.Error import Error
from orwynn.log.Log import Log
from orwynn.log.LogMiddleware import LogMiddleware
from orwynn.module.Module import Module
from orwynn.testing import Writer
from orwynn.testing.Client import Client


def __check_log_message(message: str) -> dict:
    data: dict = json.loads(str(message))
    extra: dict = data["record"]["extra"]

    request_or_response: Literal["request", "response"]
    if "request" in extra and not "response" in extra:
        request_or_response = "request"
        request_data: dict = extra["request"]
        assert type(request_data["id"]) is str
        assert type(request_data["url"]) is str
    elif "response" in extra and not "request" in extra:
        request_or_response = "request"
        response_data: dict = extra["request"]
        assert type(response_data["request_id"]) is str
        assert type(response_data["status_code"]) is int
        assert type(response_data["media_type"]) is str
    else:
        raise AssertionError()

    assert type(extra[request_or_response]["headers"]) is dict
    assert extra[request_or_response]["json"] is None or (
        # Empty json dict is not allowed in log extra - it should be replaced
        # with None.
        type(extra["json"]) is dict and extra["json"] != {}
    )

    return data


def test_get(
    writer: Writer,
    log_apprc_sink_to_writer: dict
):
    RETURNED_DATA: dict = {"hello": 1}

    class C1(HTTPController):
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

    data: dict = __check_log_message(writer.read())
    extra: dict = data["record"]["extra"]
    if "request" in extra:
        assert extra["request"]["json"] is None
    elif "response" in extra:
        assert extra["response"]["json"] == RETURNED_DATA

    Log.remove()


def test_get__error(
    writer: Writer,
    log_apprc_sink_to_writer: dict
):
    class C1(HTTPController):
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

    data: dict = __check_log_message(writer.read())
    extra: dict = data["record"]["extra"]
    if "request" in extra:
        assert extra["request"]["json"] is None
    elif "response" in extra:
        assert extra["response"]["json"] == Error("hello").api

    Log.remove()
