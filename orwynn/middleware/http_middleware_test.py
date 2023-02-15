from typing import Callable

from orwynn.boot.Boot import Boot
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.controller.http.HttpController import HttpController
from orwynn.middleware.HttpMiddleware import HttpMiddleware
from orwynn.module.Module import Module
from orwynn.testing.Client import Client
from orwynn.web import Request, Response, TestResponse


class Mw1(HttpMiddleware):
    async def process(
        self, request: Request, call_next: Callable
    ) -> Response:
        response: Response = await call_next(request)
        response.headers["x-test"] = "hello"
        return response


def test_basic():
    """
    Should work in general cases.
    """
    class C1(HttpController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self):
            return {"message": "hello"}

    boot: Boot = Boot(Module(
        route="/hello/world",
        Controllers=[C1],
        Middleware=[Mw1]
    ))
    http: Client = boot.app.client
    response: TestResponse = http.get("/hello/world")

    assert response.headers["x-test"] == "hello"


def test_variable_route():
    """Should work with variable routes.
    """
    class C1(HttpController):
        ROUTE = "/{id}"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self, id: str):
            return {"value": id}

    boot: Boot = Boot(Module(
        route="/",
        Controllers=[C1],
        Middleware=[Mw1]
    ))
    http: Client = boot.app.client
    response: TestResponse = http.get("/e201")

    assert response.json()["value"] == "e201"
    assert response.headers["x-test"] == "hello"


def test_file_path_route():
    """Should be OK with file paths.
    """
    class C1(HttpController):
        ROUTE = "/{file_path:path}"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self, file_path: str):
            return {"value": file_path}

    boot: Boot = Boot(Module(
        route="/",
        Controllers=[C1],
        Middleware=[Mw1]
    ))
    http: Client = boot.app.client
    response: TestResponse = http.get("/doc/pdf/1234.pdf")

    assert response.json()["value"] == "doc/pdf/1234.pdf"
    assert response.headers["x-test"] == "hello"
