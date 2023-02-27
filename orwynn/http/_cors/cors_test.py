from orwynn.boot._Boot import Boot
from orwynn.base.controller.endpoint.Endpoint import Endpoint
from orwynn.base.controller.http.HttpController import HttpController
from orwynn.base.module.Module import Module
from orwynn.testing._Client import Client
from orwynn.web.http.Cors import Cors


def test_basic():
    class C1(HttpController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

    def get(self):
        return {}

    boot: Boot = Boot(
        Module(route="/", Controllers=[C1]),
        cors=Cors(
            allow_origins=["*"]
        )
    )
    http: Client = boot.app.client

    r = http.options(
        "/",
        headers={
            "origin": "hello",
            "access-control-request-method": "POST"
        }
    )

    assert r.headers.get("access-control-allow-origin") == "*"


def test_correct_origin():
    class C1(HttpController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self) -> dict:
            return {}

    boot: Boot = Boot(
        Module(route="/", Controllers=[C1]),
        cors=Cors(
            allow_origins=["hello"]
        )
    )
    http: Client = boot.app.client


    r = http.options(
        "/",
        headers={
            "origin": "hello",
            "access-control-request-method": "POST"
        }
    )

    assert r.headers.get("access-control-allow-origin") == "hello"


def test_wrong_origin():
    class C1(HttpController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

    boot: Boot = Boot(
        Module(route="/", Controllers=[C1]),
        cors=Cors(
            allow_origins=["nothello"]
        )
    )
    http: Client = boot.app.client

    r = http.options(
        "/",
        headers={
            "origin": "hello",
            "access-control-request-method": "POST"
        }
    )

    assert r.headers.get("access-control-allow-origin") is None
