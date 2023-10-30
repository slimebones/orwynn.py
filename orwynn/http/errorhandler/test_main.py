import pytest

from orwynn.base.error.errors import ExceptionAlreadyHandledError
from orwynn.base.errorhandler import ErrorHandler
from orwynn.base.module import Module
from orwynn.base.service.service import Service
from orwynn.boot.boot import Boot
from orwynn.http.context.middleware.contextbuiltin import (
    HttpRequestContextBuiltinMiddleware,
)
from orwynn.http.controller.controller import HttpController
from orwynn.http.controller.endpoint.endpoint import Endpoint
from orwynn.http.middleware.middleware import HttpMiddleware
from orwynn.http.middleware.nextcall import HttpNextCall
from orwynn.http.requests import HttpRequest
from orwynn.http.responses import (
    HttpResponse,
    JsonHttpResponse,
    TestHttpResponse,
)
from orwynn.proxy.boot import BootProxy
from orwynn.testing import Client
from orwynn.testingtools import Item
from orwynn.utils import validation


class GeneralEh(ErrorHandler):
    E = Exception

    def handle(
        self, request: HttpRequestContextBuiltinMiddleware, error: Exception
    ):
        return JsonHttpResponse(
            BootProxy.ie().api_indication.digest(error),
            401
        )


class RaiseErrorController(HttpController):
    Route = "/"
    Endpoints = [Endpoint(method="get")]

    def get(self):
        raise ValueError("hello")


@pytest.mark.asyncio
async def test_custom_handler():
    class C1(HttpController):
        Route = "/"
        Endpoints = [Endpoint(method="get")]

        def get(self):
            raise ValueError("whoops!")

    boot: Boot = await Boot.create(
        Module(route="/", Controllers=[C1]),
        ErrorHandlers={GeneralEh}
    )
    http: Client = boot.app.client

    r: TestHttpResponse = http.get("/", 401)

    recovered_error: ValueError = validation.apply(
        BootProxy.ie().api_indication.recover(ValueError, r.json()),
        ValueError
    )

    assert recovered_error.args[0] == "whoops!"


@pytest.mark.asyncio
async def test_default_exception():
    class C1(HttpController):
        Route = "/"
        Endpoints = [Endpoint(method="get")]

        def get(self):
            raise TypeError("whoops!")

    boot: Boot = await Boot.create(
        Module(route="/", Controllers=[C1])
    )
    http: Client = boot.app.client

    r: TestHttpResponse = http.get("/", 400)

    recovered_exception: TypeError = validation.apply(
        BootProxy.ie().api_indication.recover(TypeError, r.json()),
        TypeError
    )

    assert recovered_exception.args[0] == "whoops!"


@pytest.mark.asyncio
async def test_as_acceptor():
    """
    Tests if an error handler can truly accept Providers.
    """
    ASSERTED_TEXT: str = "Hello, world!"

    class CoolService(Service):
        def do_something(
            self
        ) -> str:
            return ASSERTED_TEXT

    class C1(HttpController):
        Route = "/"
        Endpoints = [Endpoint(method="get")]

        def get(self):
            raise TypeError("whoops!")

    class Eh1(ErrorHandler):
        E = Exception

        def __init__(self, cool_service: CoolService) -> None:
            self.__cool_service: CoolService = cool_service

        def handle(
            self,
            request: HttpRequest,
            error: Exception
        ) -> HttpResponse:
            data: dict = BootProxy.ie().api_indication.digest(error)
            data["__test_meta_info"] = self.__cool_service.do_something()
            return JsonHttpResponse(data, 400)

    boot: Boot = await Boot.create(
        Module(route="/", Providers=[CoolService], Controllers=[C1]),
        ErrorHandlers={Eh1}
    )
    client: Client = boot.app.client

    data: dict = client.get_jsonify("/", 400)

    assert data["__test_meta_info"] == ASSERTED_TEXT


@pytest.mark.asyncio
async def test_default_in_middleware():
    """
    Should handle exceptions occured in middleware.
    """
    class C1(HttpController):
        Route = "/"
        Endpoints = [Endpoint(method="get")]

        def get(self):
            return {}

    class M1(HttpMiddleware):
        async def process(
            self,
            request: HttpRequest,
            call_next: HttpNextCall
        ) -> HttpResponse:
            raise ValueError("whoops!")

    boot: Boot = await Boot.create(
        Module(route="/", Controllers=[C1], Middleware=[M1])
    )

    r: TestHttpResponse = boot.app.client.get("/", 400)

    recovered_exception: Exception = validation.apply(
        BootProxy.ie().api_indication.recover(Exception, r.json()),
        Exception
    )

    assert recovered_exception.args[0] == "whoops!"


@pytest.mark.asyncio
async def test_custom_in_middleware():
    """
    Should handle exceptions occured in middleware.
    """
    class C1(HttpController):
        Route = "/"
        Endpoints = [Endpoint(method="get")]

        def get(self):
            return {}

    class M1(HttpMiddleware):
        async def process(
            self,
            request: HttpRequest,
            call_next: HttpNextCall
        ) -> HttpResponse:
            raise ValueError("whoops!")

    boot: Boot = await Boot.create(
        Module(route="/", Controllers=[C1], Middleware=[M1]),
        ErrorHandlers={GeneralEh}
    )

    r: TestHttpResponse = boot.app.client.get("/", 401)

    recovered: ValueError = validation.apply(
        BootProxy.ie().api_indication.recover(ValueError, r.json()),
        ValueError
    )

    assert recovered.args[0] == "whoops!"


@pytest.mark.asyncio
async def test_exception_handled_twice():
    """
    Should raise an error for twice-handled exceptions.
    """
    class Eh1(ErrorHandler):
        E = Exception

    await validation.expect_async(
        Boot.create(
            Module("/", Controllers=[RaiseErrorController]),
            ErrorHandlers={GeneralEh, Eh1}
        ),
        ExceptionAlreadyHandledError
    )


@pytest.mark.asyncio
async def test_pydantic_validation_error_is_catched():
    """
    Should catch pydantic.ValidationError too, despite it's internal multiple
    inheritance.
    """
    class _Ctrl(HttpController):
        Route = "/"
        Endpoints = [
            Endpoint(method="get")
        ]

        def get(self) -> dict:
            # Invoke a validation error
            Item(name="item", price="whocares")  # type: ignore
            return {}

    boot: Boot = await Boot.create(
        Module("/", Controllers=[_Ctrl])
    )

    boot.app.client.get_jsonify("/", 400)
