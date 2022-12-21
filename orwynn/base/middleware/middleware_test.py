from typing import Callable
from orwynn.base.controller.Controller import Controller
from orwynn.base.middleware.Middleware import Middleware
from orwynn.base.module.Module import Module
from orwynn.base.test.HttpClient import HttpClient
from orwynn.boot.Boot import Boot
from orwynn.util.http import Request, Response


def test_tmp():
    class Mw1(Middleware):
        async def process(
            self, request: Request, call_next: Callable
        ) -> Response:
            return await super().process(request, call_next)

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
    http.get_jsonify("/hello/world")

    assert False
