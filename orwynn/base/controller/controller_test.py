from orwynn.app.AlreadyRegisteredMethodError import \
    AlreadyRegisteredMethodError
from orwynn.base.controller.Controller import Controller
from orwynn.base.controller.DefinedTwiceControllerMethodError import \
    DefinedTwiceControllerMethodError
from orwynn.base.controller.endpoint import Endpoint
from orwynn.base.controller.missing_controller_class_attribute_error import \
    MissingControllerClassAttributeError
from orwynn.base.model.Model import Model
from orwynn.base.module.Module import Module
from orwynn.base.test.HttpClient import HttpClient
from orwynn.boot.Boot import Boot
from orwynn.proxy.BootProxy import BootProxy
from orwynn.util import validation
from orwynn.util.validation import (RequestValidationException, expect,
                                    validate_re)
from orwynn.util.validation.re_validation_error import ReValidationError
from orwynn.util.validation.validation_error import ValidationError
from orwynn.util.web import HTTPException, HTTPMethod
from orwynn.util.web.UnsupportedHTTPMethodError import \
    UnsupportedHTTPMethodError
from tests.std.text import DEFAULT_ID, Text


def test_http_methods():
    for method in HTTPMethod:
        assert hasattr(Controller, method.value)


def test_undefined_route():
    class C1(Controller):
        ENDPOINTS = [Endpoint(method="get")]

    m1 = Module(route="/", Controllers=[C1])
    expect(Boot, MissingControllerClassAttributeError, m1)


def test_invalid_route():
    class C1(Controller):
        ROUTE = "i don't like rules"
        ENDPOINTS = [Endpoint(method="get")]

    m1 = Module(route="/", Controllers=[C1])
    expect(Boot, ReValidationError, m1)


def test_undefined_endpoints():
    class C1(Controller):
        ROUTE = "/c1"

    m1 = Module(route="/", Controllers=[C1])
    expect(Boot, MissingControllerClassAttributeError, m1)


def test_empty_endpoints():
    class C1(Controller):
        ROUTE = "/c1"
        ENDPOINTS = []

    m1 = Module(route="/", Controllers=[C1])
    expect(Boot, ValidationError, m1)


def test_unsupported_method():
    class C1(Controller):
        ROUTE = "/c1"
        ENDPOINTS = [Endpoint(method="donuts")]

    m1 = Module(route="/", Controllers=[C1])
    expect(Boot, UnsupportedHTTPMethodError, m1)


def test_defined_twice_method():
    class C1(Controller):
        ROUTE = "/c1"
        ENDPOINTS = [Endpoint(method="get"), Endpoint(method="get")]

    m1 = Module(route="/", Controllers=[C1])
    expect(Boot, DefinedTwiceControllerMethodError, m1)


def test_uppercase_methods():
    class C1(Controller):
        ROUTE = "/c1"
        ENDPOINTS = [
            Endpoint(method="GET"),
            Endpoint(method="POST")
        ]

    m1 = Module(route="/", Controllers=[C1])
    Boot(m1)


def test_already_registered():
    class C1(Controller):
        ROUTE = "/hello"
        ENDPOINTS = [Endpoint(method="get")]

    class C2(Controller):
        ROUTE = "/hello"
        ENDPOINTS = [Endpoint(method="get")]

    m1 = Module(route="/", Controllers=[C1, C2])
    expect(Boot, AlreadyRegisteredMethodError, m1)


def test_std_routes(std_boot: Boot, std_http: HttpClient):
    json: dict = std_http.get_jsonify("/text")
    text: Text = Text.recover(json)
    validate_re(text.text, DEFAULT_ID + r"\: .+")


def test_default_404():
    class C1(Controller):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

    data: dict = Boot(
        Module(route="/", Controllers=[C1])
    ).app.http_client.get_jsonify(
        "/pizza",
        404
    )

    recovered_exception: HTTPException = validation.apply(
        BootProxy.ie().api_indication.recover(
            data
        ),
        HTTPException
    )

    assert recovered_exception.status_code == 404
    assert recovered_exception.detail == "Not Found"


def test_default_request_validation_error():
    class Item(Model):
        name: str
        price: float

    class C1(Controller):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="post")]

        def post(self, item: Item) -> dict:
            return {}

    data: dict = Boot(
        Module(route="/", Controllers=[C1])
    ).app.http_client.post_jsonify(
        "/",
        422,
        json={
            "name": 222,
            "price": "hello"
        }
    )

    # Temporarily content of this exception is not checked since is not filled
    # back in indication
    validation.apply(
        BootProxy.ie().api_indication.recover(
            data
        ),
        RequestValidationException
    )


def test_default_method_not_allowed():
    class Item(Model):
        name: str
        price: float

    class C1(Controller):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self) -> dict:
            return {}

    data: dict = Boot(
        Module(route="/", Controllers=[C1])
    ).app.http_client.post_jsonify(
        "/",
        405
    )

    recovered_exception: HTTPException = validation.apply(
        BootProxy.ie().api_indication.recover(
            data
        ),
        HTTPException
    )

    assert recovered_exception.status_code == 405
    assert recovered_exception.detail == "Method Not Allowed"
