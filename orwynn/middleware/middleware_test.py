from typing import Callable

from orwynn.boot.Boot import Boot
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.controller.http.HTTPController import HTTPController
from orwynn.middleware.Middleware import Middleware
from orwynn.module.Module import Module
from orwynn.test.Client import Client
from orwynn.web import Request, Response, TestResponse


def test_basic():
    class Mw1(Middleware):
        async def process(
            self, request: Request, call_next: Callable
        ) -> Response:
            response: Response = await call_next(request)
            response.headers["x-test"] = "hello"
            return response

    class C1(HTTPController):
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
