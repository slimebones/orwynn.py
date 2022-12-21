from typing import Callable
from orwynn.base.controller.Controller import Controller
from orwynn.base.middleware._Middleware import Middleware
from orwynn.base.module.Module import Module
from orwynn.base.test.HttpClient import HttpClient
from orwynn.boot.Boot import Boot
from orwynn.util.web import Request, Response, TestResponse


def test_basic():
    class Mw1(Middleware):
        async def process(
            self, request: Request, call_next: Callable
        ) -> Response:
            response: Response = await call_next(request)
            response.headers["x-test"] = "hello"
            return response

    class C1(Controller):
        ROUTE = "/"
        METHODS = ["get"]

        def get(self):
            return {"message": "hello"}

    boot: Boot = Boot(Module(
        route="/hello/world",
        Controllers=[C1],
        Middleware=[Mw1]
    ))
    http: HttpClient = boot.app.http_client
    response: TestResponse = http.get("/hello/world")

    assert response.headers["x-test"] == "hello"
