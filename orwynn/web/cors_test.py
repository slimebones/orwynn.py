from orwynn.boot.Boot import Boot
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.controller.http.HttpController import HttpController
from orwynn.module.Module import Module
from orwynn.testing.Client import Client
from orwynn.web.CORS import CORS


def test_basic():
    class C1(HttpController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

    def get(self):
        return {}

    boot: Boot = Boot(
        Module(route="/", Controllers=[C1]),
        cors=CORS(
            allow_origins=["*"]
        )
    )
    http: Client = boot.app.client

    r = http.options("/", headers={"origin": "hello"})

    assert r.headers.get("access-control-allow-origin") == "*"


def test_correct_origin():
    class C1(HttpController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self) -> dict:
            return {}

    boot: Boot = Boot(
        Module(route="/", Controllers=[C1]),
        cors=CORS(
            allow_origins=["hello"]
        )
    )
    http: Client = boot.app.client

    r = http.options("/", headers={"origin": "hello"})

    assert r.headers.get("access-control-allow-origin") == "hello"


def test_wrong_origin():
    class C1(HttpController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

    boot: Boot = Boot(
        Module(route="/", Controllers=[C1]),
        cors=CORS(
            allow_origins=["nothello"]
        )
    )
    http: Client = boot.app.client

    r = http.options("/", headers={"origin": "hello"})

    assert r.headers.get("access-control-allow-origin") is None
