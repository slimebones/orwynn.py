from typing import Callable

from orwynn.src.boot.Boot import Boot
from orwynn.src.controller.endpoint.Endpoint import Endpoint
from orwynn.src.controller.http.HttpController import HttpController
from orwynn.src.middleware.HttpMiddleware import HttpMiddleware
from orwynn.src.module.Module import Module
from orwynn.src.testing.Client import Client
from orwynn.src.web.http.requests import HttpRequest
from orwynn.src.web.http.responses import HttpResponse, TestHttpResponse


class Mw1(HttpMiddleware):
    async def process(
        self, request: HttpRequest, call_next: Callable
    ) -> HttpResponse:
        response: HttpResponse = await call_next(request)
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
    response: TestHttpResponse = http.get("/hello/world")

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
    response: TestHttpResponse = http.get("/e201")

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
    response: TestHttpResponse = http.get("/doc/pdf/1234.pdf")

    assert response.json()["value"] == "doc/pdf/1234.pdf"
    assert response.headers["x-test"] == "hello"
