from orwynn.app.already_registered_route_error import \
    AlreadyRegisteredRouteError
from orwynn.base.controller.controller import Controller
from orwynn.base.controller.defined_twice_controller_method_error import \
    DefinedTwiceControllerMethodError
from orwynn.base.controller.missing_controller_class_attribute_error import \
    MissingControllerClassAttributeError
from orwynn.base.module.module import Module
from orwynn.base.test.http_client import HttpClient
from orwynn.boot.boot import Boot
from orwynn.http import HTTPMethod, TestResponse
from orwynn.http.unsupported_http_method_error import \
    UnsupportedHTTPMethodError
from orwynn.util.expect import expect
from orwynn.validation.validation_error import ReValidationError, ValidationError


def test_http_methods():
    for method in HTTPMethod:
        assert hasattr(Controller, method.value)


def test_undefined_route():
    class C1(Controller):
        METHODS = ["get"]

    m1 = Module(route="/", Controllers=[C1])
    expect(Boot, MissingControllerClassAttributeError, m1)


def test_invalid_route():
    class C1(Controller):
        ROUTE = "i don't like rules"
        METHODS = ["get"]

    m1 = Module(route="/", Controllers=[C1])
    expect(Boot, ReValidationError, m1)


def test_undefined_methods():
    class C1(Controller):
        ROUTE = "/c1"

    m1 = Module(route="/", Controllers=[C1])
    expect(Boot, MissingControllerClassAttributeError, m1)


def test_empty_methods():
    class C1(Controller):
        ROUTE = "/c1"
        METHODS = []

    m1 = Module(route="/", Controllers=[C1])
    expect(Boot, ValidationError, m1)


def test_unsupported_method():
    class C1(Controller):
        ROUTE = "/c1"
        METHODS = ["donuts"]

    m1 = Module(route="/", Controllers=[C1])
    expect(Boot, UnsupportedHTTPMethodError, m1)


def test_defined_twice_method():
    class C1(Controller):
        ROUTE = "/c1"
        METHODS = ["get", "post", "get"]

    m1 = Module(route="/", Controllers=[C1])
    expect(Boot, DefinedTwiceControllerMethodError, m1)


def test_uppercase_methods():
    class C1(Controller):
        ROUTE = "/c1"
        METHODS = ["GET", "POST"]

    m1 = Module(route="/", Controllers=[C1])
    Boot(m1)


def test_already_registered():
    class C1(Controller):
        ROUTE = "/hello"
        METHODS = ["get"]

    class C2(Controller):
        ROUTE = "/hello"
        METHODS = ["get"]

    m1 = Module(route="/", Controllers=[C1, C2])
    expect(Boot, AlreadyRegisteredRouteError, m1)


def test_std_routes(std_boot: Boot, std_http: HttpClient):
    r: TestResponse = std_http.get("/text")
    assert False, r
