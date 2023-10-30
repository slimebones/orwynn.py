from typing import Callable

import pytest

from orwynn.base.module.module import Module
from orwynn.boot.boot import Boot
from orwynn.http import (
    Endpoint,
    HttpController,
    HttpMiddleware,
    HttpRequest,
    HttpResponse,
    TestHttpResponse,
)
from orwynn.testing.client import Client


class Mw1(HttpMiddleware):
    async def process(
        self, request: HttpRequest, call_next: Callable
    ) -> HttpResponse:
        response: HttpResponse = await call_next(request)
        response.headers["x-test"] = "hello"
        return response


@pytest.mark.asyncio
async def test_basic():
    """
    Should work in general cases.
    """
    class C1(HttpController):
        Route = "/"
        Endpoints = [Endpoint(method="get")]

        def get(self):
            return {"message": "hello"}

    boot: Boot = await Boot.create(Module(
        route="/hello/world",
        Controllers=[C1],
        Middleware=[Mw1]
    ))
    http: Client = boot.app.client
    response: TestHttpResponse = http.get("/hello/world")

    assert response.headers["x-test"] == "hello"


@pytest.mark.asyncio
async def test_variable_route():
    """Should work with variable routes.
    """
    class C1(HttpController):
        Route = "/{id}"
        Endpoints = [Endpoint(method="get")]

        def get(self, id: str):
            return {"value": id}

    boot: Boot = await Boot.create(Module(
        route="/",
        Controllers=[C1],
        Middleware=[Mw1]
    ))
    http: Client = boot.app.client
    response: TestHttpResponse = http.get("/e201")

    assert response.json()["value"] == "e201"
    assert response.headers["x-test"] == "hello"


@pytest.mark.asyncio
async def test_file_path_route():
    """Should be OK with file paths.
    """
    class C1(HttpController):
        Route = "/{file_path:path}"
        Endpoints = [Endpoint(method="get")]

        def get(self, file_path: str):
            return {"value": file_path}

    boot: Boot = await Boot.create(Module(
        route="/",
        Controllers=[C1],
        Middleware=[Mw1]
    ))
    http: Client = boot.app.client
    response: TestHttpResponse = http.get("/doc/pdf/1234.pdf")

    assert response.json()["value"] == "doc/pdf/1234.pdf"
    assert response.headers["x-test"] == "hello"
