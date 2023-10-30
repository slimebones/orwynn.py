
import pytest
from fastapi import Query, Request

from orwynn.apiversion import ApiVersion
from orwynn.base.controller.errors import (
    AlreadyRegisteredMethodError,
    MissingControllerClassAttributeError,
)
from orwynn.base.model import Model
from orwynn.base.module import Module
from orwynn.boot import Boot
from orwynn.di.di import Di
from orwynn.helpers.web import REQUEST_METHOD_BY_PROTOCOL
from orwynn.http import Endpoint, HttpController
from orwynn.http.controller.errors import DefinedTwiceControllerMethodError
from orwynn.http.errors import HttpException, UnsupportedHttpMethodError
from orwynn.proxy.boot import BootProxy
from orwynn.testing import Client
from orwynn.utils import validation
from orwynn.utils.scheme import Scheme
from orwynn.utils.validation import validate_re
from orwynn.utils.validation.errors import (
    RequestValidationException,
    ReValidationError,
    ValidationError,
)
from tests.std.text import DEFAULT_ID, Text


def test_http_methods():
    for method in REQUEST_METHOD_BY_PROTOCOL[Scheme.HTTP]:
        assert hasattr(HttpController, method.value)


@pytest.mark.asyncio
async def test_undefined_route():
    class C1(HttpController):
        Endpoints = [Endpoint(method="get")]

    m1 = Module(route="/", Controllers=[C1])
    await validation.expect_async(
        Boot.create(m1),
        MissingControllerClassAttributeError
    )


@pytest.mark.asyncio
async def test_invalid_route():
    class C1(HttpController):
        Route = "i don't like rules"
        Endpoints = [Endpoint(method="get")]

    m1 = Module(route="/", Controllers=[C1])
    await validation.expect_async(
        Boot.create(m1),
        ReValidationError
    )


@pytest.mark.asyncio
async def test_undefined_endpoints():
    class C1(HttpController):
        Route = "/c1"

    m1 = Module(route="/", Controllers=[C1])
    await validation.expect_async(
        Boot.create(m1),
        MissingControllerClassAttributeError
    )


@pytest.mark.asyncio
async def test_empty_endpoints():
    class C1(HttpController):
        Route = "/c1"
        Endpoints = []

    m1 = Module(route="/", Controllers=[C1])
    await validation.expect_async(
        Boot.create(m1),
        ValidationError
    )


@pytest.mark.asyncio
async def test_unsupported_method():
    class C1(HttpController):
        Route = "/c1"
        Endpoints = [Endpoint(method="donuts")]

    m1 = Module(route="/", Controllers=[C1])
    await validation.expect_async(
        Boot.create(m1),
        UnsupportedHttpMethodError
    )


@pytest.mark.asyncio
async def test_defined_twice_method():
    class C1(HttpController):
        Route = "/c1"
        Endpoints = [Endpoint(method="get"), Endpoint(method="get")]

    m1 = Module(route="/", Controllers=[C1])
    await validation.expect_async(
        Boot.create(m1),
        DefinedTwiceControllerMethodError
    )


@pytest.mark.asyncio
async def test_uppercase_methods():
    class C1(HttpController):
        Route = "/c1"
        Endpoints = [
            Endpoint(method="GET"),
            Endpoint(method="POST")
        ]

    m1 = Module(route="/", Controllers=[C1])
    await Boot.create(m1)


@pytest.mark.asyncio
async def test_already_registered():
    class C1(HttpController):
        Route = "/hello"
        Endpoints = [Endpoint(method="get")]

    class C2(HttpController):
        Route = "/hello"
        Endpoints = [Endpoint(method="get")]

    m1 = Module(route="/", Controllers=[C1, C2])
    await validation.expect_async(
        Boot.create(m1),
        AlreadyRegisteredMethodError
    )


def test_std_routes(std_boot: Boot, std_http: Client):
    json: dict = std_http.get_jsonify("/text")
    text: Text = Text.recover(json)
    validate_re(text.text, DEFAULT_ID + r"\: .+")


@pytest.mark.asyncio
async def test_default_404():
    class C1(HttpController):
        Route = "/"
        Endpoints = [Endpoint(method="get")]

    boot: Boot = await Boot.create(
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


@pytest.mark.asyncio
async def test_default_request_validation_error():
    class Item(Model):
        name: str
        price: float

    class C1(HttpController):
        Route = "/"
        Endpoints = [Endpoint(method="post")]

        def post(self, item: Item) -> dict:
            return {}

    data: dict = (await Boot.create(
        Module(route="/", Controllers=[C1])
    )).app.client.post_jsonify(
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


@pytest.mark.asyncio
async def test_default_method_not_allowed():
    class C1(HttpController):
        Route = "/"
        Endpoints = [Endpoint(method="get")]

        def get(self) -> dict:
            return {}

    data: dict = (await Boot.create(
        Module(route="/", Controllers=[C1])
    )).app.client.post_jsonify(
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


@pytest.mark.asyncio
async def test_final_routes():
    class _Ctrl(HttpController):
        Route = "/{id}/tasty"
        Endpoints = [
            Endpoint(method="get")
        ]

    await Boot.create(
        Module("/donuts", Controllers=[_Ctrl]),
        global_http_route="/api/v{version}"
    )

    ctrl: HttpController = validation.apply(
        Di.ie().find("_Ctrl"),
        HttpController
    )

    assert "/api/v1/donuts/{id}/tasty" in ctrl.final_routes


@pytest.mark.asyncio
async def test_is_matching_route():
    class _Ctrl(HttpController):
        Route = "/{id}/tasty"
        Endpoints = [
            Endpoint(method="get")
        ]
        Version = 2

    await Boot.create(
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


@pytest.mark.asyncio
async def test_multiple_query_params():
    """
    Should correctly parse list of query params.
    """
    class _Ctrl(HttpController):
        Route = "/items"
        Endpoints = [
            Endpoint(method="get")
        ]

        def get(
            self,
            request: Request,
            q: list[str] | None = Query(None)
        ) -> dict:
            return {
                "q": q
            }

    boot: Boot = await Boot.create(
        Module("/", Controllers=[_Ctrl])
    )

    data: dict = boot.client.get_jsonify(
        "/items?q=1&q=2",
        200
    )

    assert data == {
        "q": ["1", "2"]
    }
