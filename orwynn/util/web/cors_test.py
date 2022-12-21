from orwynn.base.controller.Controller import Controller
from orwynn.base.module.Module import Module
from orwynn.base.test.HttpClient import HttpClient
from orwynn.boot.Boot import Boot
from orwynn.util.web._CORS import CORS


def test_basic():
    class C1(Controller):
        ROUTE = "/"
        METHODS = ["get"]

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
    class C1(Controller):
        ROUTE = "/"
        METHODS = ["get"]

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
    class C1(Controller):
        ROUTE = "/"
        METHODS = ["get"]

    def get(self):
        return {}

    boot: Boot = Boot(
        Module(route="/", Controllers=[C1]),
        cors=CORS(
            allow_origins=["nothello"]
        )
    )
    http: HttpClient = boot.app.http_client

    r = http.options("/", headers={"origin": "hello"})

    assert r.headers.get("access-control-allow-origin") is None
