from orwynn import web
from orwynn.boot.Boot import Boot
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.controller.http.HTTPController import HTTPController
from orwynn.module.Module import Module


def test_basic():
    class C1(HTTPController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self) -> dict:
            print(web.context)
            return {"message": "hello"}

    boot: Boot = Boot(
        Module(
            "/",
            Controllers=[C1]
        )
    )

    boot.app.client.get("/", 200)
    assert 0
