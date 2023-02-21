from orwynn import validation
from orwynn.src.app.AlreadyRegisteredMethodError import (
    AlreadyRegisteredMethodError,
)
from orwynn.src.boot.Boot import Boot
from orwynn.src.controller.endpoint.Endpoint import Endpoint
from orwynn.src.controller.http.DefinedTwiceControllerMethodError import (
    DefinedTwiceControllerMethodError,
)
from orwynn.src.controller.http.HttpController import HttpController
from orwynn.src.controller.MissingControllerClassAttributeError import (
    MissingControllerClassAttributeError,
)
from orwynn.src.model.Model import Model
from orwynn.src.module.Module import Module
from orwynn.src.proxy.BootProxy import BootProxy
from orwynn.src.testing.Client import Client
from orwynn.src.validation import RequestValidationException, expect, validate_re
from orwynn.src.validation.re_validation_error import ReValidationError
from orwynn.src.validation.ValidationError import ValidationError
from orwynn.src.web.http.HttpException import HttpException
from orwynn.src.web.http.HttpMethod import HttpMethod
from orwynn.src.web.http.UnsupportedHttpMethodError import (
    UnsupportedHttpMethodError,
)
from tests.std.text import DEFAULT_ID, Text


def test_http_methods():
    for method in HttpMethod:
        assert hasattr(HttpController, method.value)


def test_undefined_route():
    class C1(HttpController):
        ENDPOINTS = [Endpoint(method="get")]

    m1 = Module(route="/", Controllers=[C1])
    expect(Boot, MissingControllerClassAttributeError, m1)


def test_invalid_route():
    class C1(HttpController):
        ROUTE = "i don't like rules"
        ENDPOINTS = [Endpoint(method="get")]

    m1 = Module(route="/", Controllers=[C1])
    expect(Boot, ReValidationError, m1)


def test_undefined_endpoints():
    class C1(HttpController):
        ROUTE = "/c1"

    m1 = Module(route="/", Controllers=[C1])
    expect(Boot, MissingControllerClassAttributeError, m1)


def test_empty_endpoints():
    class C1(HttpController):
        ROUTE = "/c1"
        ENDPOINTS = []

    m1 = Module(route="/", Controllers=[C1])
    expect(Boot, ValidationError, m1)


def test_unsupported_method():
    class C1(HttpController):
        ROUTE = "/c1"
        ENDPOINTS = [Endpoint(method="donuts")]

    m1 = Module(route="/", Controllers=[C1])
    expect(Boot, UnsupportedHttpMethodError, m1)


def test_defined_twice_method():
    class C1(HttpController):
        ROUTE = "/c1"
        ENDPOINTS = [Endpoint(method="get"), Endpoint(method="get")]

    m1 = Module(route="/", Controllers=[C1])
    expect(Boot, DefinedTwiceControllerMethodError, m1)


def test_uppercase_methods():
    class C1(HttpController):
        ROUTE = "/c1"
        ENDPOINTS = [
            Endpoint(method="GET"),
            Endpoint(method="POST")
        ]

    m1 = Module(route="/", Controllers=[C1])
    Boot(m1)


def test_already_registered():
    class C1(HttpController):
        ROUTE = "/hello"
        ENDPOINTS = [Endpoint(method="get")]

    class C2(HttpController):
        ROUTE = "/hello"
        ENDPOINTS = [Endpoint(method="get")]

    m1 = Module(route="/", Controllers=[C1, C2])
    expect(Boot, AlreadyRegisteredMethodError, m1)


def test_std_routes(std_boot: Boot, std_http: Client):
    json: dict = std_http.get_jsonify("/text")
    text: Text = Text.recover(json)
    validate_re(text.text, DEFAULT_ID + r"\: .+")


def test_default_404():
    class C1(HttpController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

    boot: Boot = Boot(
        Module(route="/", Controllers=[C1])
    )

    data: dict = boot.app.client.get_jsonify(
        "/pizza",
        404
    )

    recovered_exception: HttpException = validation.apply(
        BootProxy.ie().api_indication.recover(
            HttpException,
            data
        ),
        HttpException
    )

    assert recovered_exception.status_code == 404
    assert recovered_exception.detail == "Not Found"


def test_default_request_validation_error():
    class Item(Model):
        name: str
        price: float

    class C1(HttpController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="post")]

        def post(self, item: Item) -> dict:
            return {}

    data: dict = Boot(
        Module(route="/", Controllers=[C1])
    ).app.client.post_jsonify(
        "/",
        422,
        json={
            "name": 222,
            "price": "hello"
        }
    )

    # Temporarily content of this exception is not checked since it is not
    # filled back to the indication
    validation.apply(
        BootProxy.ie().api_indication.recover(
            RequestValidationException,
            data
        ),
        RequestValidationException
    )


def test_default_method_not_allowed():
    class C1(HttpController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self) -> dict:
            return {}

    data: dict = Boot(
        Module(route="/", Controllers=[C1])
    ).app.client.post_jsonify(
        "/",
        405
    )

    recovered_exception: HttpException = validation.apply(
        BootProxy.ie().api_indication.recover(
            HttpException,
            data
        ),
        HttpException
    )

    assert recovered_exception.status_code == 405
    assert recovered_exception.detail == "Method Not Allowed"
