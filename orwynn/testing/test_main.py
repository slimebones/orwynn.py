import pytest
from fastapi import Header

from orwynn.base.module.module import Module
from orwynn.boot import Boot
from orwynn.http import Endpoint, HttpController
from orwynn.testing.client import Client
from orwynn.testingtools import HeadersGetController


class _Ctrl1(HttpController):
    Route = "/"
    Endpoints = [
        Endpoint(method="get")
    ]

    def get(self, x_testing: str | None = Header(default=None)) -> dict:
        return {
            "x-testing": x_testing or None
        }


class _Ctrl2(HttpController):
    Route = "/"
    Endpoints = [
        Endpoint(method="get")
    ]

    def get(
        self,
        x_testing: str | None = Header(default=None),
        x_tmp: str | None = Header(default=None)
    ) -> dict:
        return {
            "x-testing": x_testing or None,
            "x-tmp": x_tmp or None
        }


@pytest.mark.asyncio
async def test_bind_headers():
    boot: Boot = await Boot.create(
        Module("/", Controllers=[_Ctrl1])
    )

    binded: Client = boot.app.client.bind_headers({
        "x-testing": "hello"
    })

    data: dict = binded.get_jsonify("/")
    assert data["x-testing"] == "hello"


@pytest.mark.asyncio
async def test_bind_headers_accumulate():
    boot: Boot = await Boot.create(
        Module("/", Controllers=[_Ctrl2])
    )

    binded: Client = boot.app.client.bind_headers({
        "x-testing": "hello"
    }).bind_headers({
        "x-tmp": "world"
    })

    data: dict = binded.get_jsonify("/")
    assert data["x-testing"] == "hello"
    assert data["x-tmp"] == "world"

@pytest.mark.asyncio
async def test_multiple_bind_headers():
    """
    Shouldn't stack bind headers in the original client for subsequent
    bind_headers() calls.
    """
    boot: Boot = await Boot.create(
        Module("/", Controllers=[HeadersGetController])
    )

    binded_1: Client = boot.app.client.bind_headers({
        "x-testing": "hello"
    })

    binded_2: Client = binded_1.bind_headers({
        "x-tmp": "world"
    })

    assert binded_1.binded_headers == {"x-testing": "hello"}
    assert binded_2.binded_headers == {
        "x-testing": "hello",
        "x-tmp": "world"
    }
