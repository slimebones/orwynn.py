from orwynn.app.already_registered_route_error import AlreadyRegisteredRouteError
from orwynn.base.controller.controller import Controller
from orwynn.base.module.module import Module
from orwynn.base.test.http_client import HttpClient
from orwynn.boot.boot import Boot
from orwynn.http import HTTPMethod, TestResponse
from orwynn.util.expect import expect


def test_http_methods():
    for method in HTTPMethod:
        assert hasattr(Controller, method.value)


# def test_std_routes(std_boot: Boot, std_http: HttpClient):
#     r: TestResponse = std_http.get("/text")
#     assert False, r


def test_already_registered():
    class C1(Controller):
        ROUTE = "/hello"

    class C2(Controller):
        ROUTE = "/hello"

    m1 = Module(route="/", Controllers=[C1, C2])

    expect(Boot, AlreadyRegisteredRouteError, m1)
