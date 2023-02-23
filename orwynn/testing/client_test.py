
from fastapi import Header

from orwynn.boot.Boot import Boot
from orwynn.http import Endpoint, HttpController
from orwynn.base.module.Module import Module
from orwynn.testing._Client import Client


class _Ctrl1(HttpController):
    ROUTE = "/"
    ENDPOINTS = [
        Endpoint(method="get")
    ]

    def get(self, x_testing: str | None = Header(default=None)) -> dict:
        return {
            "x-testing": x_testing or None
        }


class _Ctrl2(HttpController):
    ROUTE = "/"
    ENDPOINTS = [
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


def test_bind_headers():
    boot: Boot = Boot(
        Module("/", Controllers=[_Ctrl1])
    )

    binded: Client = boot.app.client.bind_headers({
        "x-testing": "hello"
    })

    data: dict = binded.get_jsonify("/")
    assert data["x-testing"] == "hello"


def test_bind_headers_accumulate():
    boot: Boot = Boot(
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
