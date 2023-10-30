import json
from types import NoneType
from typing import Literal

import pytest

from orwynn.base.module.module import Module
from orwynn.boot.boot import Boot
from orwynn.http import Endpoint, HttpController, LogMiddleware
from orwynn.log import Log
from orwynn.proxy.boot import BootProxy
from orwynn.testing import Writer
from orwynn.testing.client import Client


def _check_log_message(message: str) -> list[dict]:
    assert message != ""
    items: list[str] = message.split("\n")
    parsed_items: list[dict] = []

    for item in items:
        if item == "":
            continue
        data: dict = json.loads(str(item))
        extra: dict = data["record"]["extra"]

        try:
            http_extra: dict = extra["http"]
        except KeyError as error:
            raise AssertionError from error

        request_or_response: Literal["request", "response"]
        if "request" in http_extra and "response" not in http_extra:
            request_or_response = "request"
            request_data: dict = http_extra["request"]
            assert type(request_data["id"]) is str
            assert type(request_data["url"]) is str
        elif "response" in http_extra and "request" not in http_extra:
            request_or_response = "response"
            response_data: dict = http_extra["response"]
            assert type(response_data["request_id"]) is str
            assert type(response_data["status_code"]) is int
            assert type(response_data["media_type"]) in [str, NoneType]
        else:
            raise AssertionError

        assert type(http_extra[request_or_response]["headers"]) is dict
        assert http_extra[request_or_response]["json"] is None or (
            # Empty json dict is not allowed in log extra - it should be
            # replaced with None.
            type(http_extra[request_or_response]["json"]) is dict
            and extra[request_or_response]["json"] != {}
        )

        parsed_items.append(data)

    return parsed_items


@pytest.mark.asyncio
async def test_get(
    writer: Writer,
    log_apprc_sink_to_writer: dict
):
    RETURNED_DATA: dict = {"hello": 1}

    class C1(HttpController):
        Route = "/"
        Endpoints = [Endpoint(method="get")]

        def get(self) -> dict:
            return RETURNED_DATA

    boot: Boot = await Boot.create(
        Module(
            route="/", Controllers=[C1], Middleware=[LogMiddleware]
        ),
        apprc=log_apprc_sink_to_writer
    )  # type: ignore #worker
    client: Client = boot.app.client
    client.get(
        "/",
        200
    )

    items: list[dict] = _check_log_message(writer.read())
    for item in items:
        extra: dict = item["record"]["extra"]
        if "request" in extra:
            assert extra["http.request"]["json"] is None
        elif "response" in extra:
            assert extra["http.response"]["json"] == RETURNED_DATA

    Log.remove()


@pytest.mark.asyncio
async def test_get__error(
    writer: Writer,
    log_apprc_sink_to_writer: dict
):
    class C1(HttpController):
        Route = "/"
        Endpoints = [Endpoint(method="get")]

        def get(self) -> dict:
            raise ValueError("hello")

    boot: Boot = await Boot.create(
        Module(
            route="/", Controllers=[C1], Middleware=[LogMiddleware]
        ),
        apprc=log_apprc_sink_to_writer
    )  # type: ignore #worker
    client: Client = boot.app.client
    client.get(
        "/",
        400
    )

    items: list[dict] = _check_log_message(writer.read())
    for item in items:
        extra: dict = item["record"]["extra"]
        if "request" in extra:
            assert extra["http.request"]["json"] is None
        elif "response" in extra:
            assert \
                extra["http.response"]["json"] \
                == BootProxy.ie().api_indication.digest(ValueError("hello"))

    Log.remove()
