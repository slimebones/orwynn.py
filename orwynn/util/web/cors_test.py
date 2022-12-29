from orwynn.boot.Boot import Boot
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.controller.http.HTTPController import HTTPController
from orwynn.module.Module import Module
from orwynn.test.HttpClient import HttpClient
from orwynn.util.web.CORS import CORS


def test_basic():
    class C1(HTTPController):
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
    http: HttpClient = boot.app.http_client

    r = http.options("/", headers={"origin": "hello"})

    assert r.headers.get("access-control-allow-origin") == "*"


def test_correct_origin():
    class C1(HTTPController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

    def get(self):
        return {}

    boot: Boot = Boot(
        Module(route="/", Controllers=[C1]),
        cors=CORS(
            allow_origins=["hello"]
        )
    )
    http: HttpClient = boot.app.http_client

    r = http.options("/", headers={"origin": "hello"})

    assert r.headers.get("access-control-allow-origin") == "hello"


def test_wrong_origin():
    class C1(HTTPController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

    boot: Boot = Boot(
        Module(route="/", Controllers=[C1]),
        cors=CORS(
            allow_origins=["nothello"]
        )
    )
    http: HttpClient = boot.app.http_client

    r = http.options("/", headers={"origin": "hello"})

    assert r.headers.get("access-control-allow-origin") is None
