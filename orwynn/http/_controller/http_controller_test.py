from orwynn._di.Di import Di
from orwynn.apiversion import ApiVersion
from orwynn.base.controller.errors import (
    AlreadyRegisteredMethodError,
    MissingControllerClassAttributeError,
)
from orwynn.base.model import Model
from orwynn.base.module import Module
from orwynn.boot import Boot
from orwynn.helpers.web import REQUEST_METHOD_BY_PROTOCOL
from orwynn.http import Endpoint, HttpController
from orwynn.http._controller.errors import DefinedTwiceControllerMethodError
from orwynn.http.errors import HttpException, UnsupportedHttpMethodError
from orwynn.proxy.BootProxy import BootProxy
from orwynn.testing import Client
from orwynn.utils import validation
from orwynn.utils.Protocol import Protocol
from orwynn.utils.validation import expect, validate_re
from orwynn.utils.validation.errors import (
    RequestValidationException,
    ReValidationError,
    ValidationError,
)
from tests.std.text import DEFAULT_ID, Text


def test_http_methods():
    for method in REQUEST_METHOD_BY_PROTOCOL[Protocol.HTTP]:
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


def test_final_routes():
    class _Ctrl(HttpController):
        ROUTE = "/{id}/tasty"
        ENDPOINTS = [
            Endpoint(method="get")
        ]

    Boot(
        Module("/donuts", Controllers=[_Ctrl]),
        global_http_route="/api/v{version}"
    )

    ctrl: HttpController = validation.apply(
        Di.ie().find("_Ctrl"),
        HttpController
    )

    assert "/api/v1/donuts/{id}/tasty" in ctrl.final_routes


def test_is_matching_route():
    class _Ctrl(HttpController):
        ROUTE = "/{id}/tasty"
        ENDPOINTS = [
            Endpoint(method="get")
        ]
        VERSION = 2

    Boot(
        Module("/donuts", Controllers=[_Ctrl]),
        global_http_route="/api/v{version}",
        api_version=ApiVersion(supported={1, 2, 3})
    )

    ctrl: HttpController = validation.apply(
        Di.ie().find("_Ctrl"),
        HttpController
    )

    assert ctrl.is_matching_route("/api/v2/donuts/e67840v/tasty") is True

    # Another versions should not be listed if a controller does not support
    # them
    assert ctrl.is_matching_route("/api/v1/donuts/e67840v/tasty") is False
    assert ctrl.is_matching_route("/api/v3/donuts/helloworld/tasty") is False
    ##

    assert ctrl.is_matching_route("/api/v2/donuts/e67840v/tasty/gogo") is False
    assert ctrl.is_matching_route("/api/v2/donuts/tasty") is False
    assert ctrl.is_matching_route("/api/donuts/eb00v/tasty") is False
    assert ctrl.is_matching_route("/donuts/eb00v/tasty") is False
