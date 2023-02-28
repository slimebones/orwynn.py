from orwynn.base.error import Error, ExceptionAlreadyHandledError
from orwynn.base.exchandler._ExceptionHandler import ExceptionHandler
from orwynn.base.module._Module import Module
from orwynn.base.service._Service import Service
from orwynn.boot._Boot import Boot
from orwynn.http._context.HttpRequestContextBuiltinMiddleware import (
    HttpRequestContextBuiltinMiddleware,
)
from orwynn.http._controller.endpoint.Endpoint import Endpoint
from orwynn.http._controller.HttpController import HttpController
from orwynn.http._middleware.HttpMiddleware import HttpMiddleware
from orwynn.http._middleware.HttpNextCall import HttpNextCall
from orwynn.http._requests import HttpRequest
from orwynn.http._responses import (
    HttpResponse,
    JsonHttpResponse,
    TestHttpResponse,
)
from orwynn.proxy.BootProxy import BootProxy
from orwynn.testing import Client
from orwynn.util import validation


class GeneralEh(ExceptionHandler):
    E = Error

    def handle(
        self, request: HttpRequestContextBuiltinMiddleware, error: Error
    ):
        return JsonHttpResponse(error.api, 401)


class RaiseErrorController(HttpController):
    ROUTE = "/"
    ENDPOINTS = [Endpoint(method="get")]

    def get(self):
        raise Error("hello")


def test_custom_handler():
    class C1(HttpController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self):
            raise Error("whoops!")

    boot: Boot = Boot(
        Module(route="/", Controllers=[C1]),
        ExceptionHandlers={GeneralEh}
    )
    http: Client = boot.app.client

    r: TestHttpResponse = http.get("/", 401)

    recovered_error: Error = validation.apply(
        BootProxy.ie().api_indication.recover(Error, r.json()),
        Error
    )

    assert recovered_error.message == "whoops!"


def test_default_exception():
    class C1(HttpController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self):
            raise TypeError("whoops!")

    boot: Boot = Boot(
        Module(route="/", Controllers=[C1])
    )
    http: Client = boot.app.client

    r: TestHttpResponse = http.get("/", 400)

    recovered_exception: Exception = validation.apply(
        BootProxy.ie().api_indication.recover(Exception, r.json()),
        Exception
    )

    assert recovered_exception.args[0] == "whoops!"


def test_as_acceptor():
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
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self):
            raise Error("whoops!")

    class Eh1(ExceptionHandler):
        E = Error

        def __init__(self, cool_service: CoolService) -> None:
            self.__cool_service: CoolService = cool_service

        def handle(self, request: HttpRequest, error: Error) -> HttpResponse:
            data: dict = error.api
            data["__test_meta_info"] = self.__cool_service.do_something()
            return JsonHttpResponse(data, 400)

    boot: Boot = Boot(
        Module(route="/", Providers=[CoolService], Controllers=[C1]),
        ExceptionHandlers={Eh1}
    )
    client: Client = boot.app.client

    data: dict = client.get_jsonify("/", 400)

    assert data["__test_meta_info"] == ASSERTED_TEXT


def test_default_in_middleware():
    """
    Should handle exceptions occured in middleware.
    """
    class C1(HttpController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self):
            return {}

    class M1(HttpMiddleware):
        async def process(
            self,
            request: HttpRequest,
            call_next: HttpNextCall
        ) -> HttpResponse:
            raise ValueError("whoops!")

    boot: Boot = Boot(
        Module(route="/", Controllers=[C1], Middleware=[M1])
    )

    r: TestHttpResponse = boot.app.client.get("/", 400)

    recovered_exception: Exception = validation.apply(
        BootProxy.ie().api_indication.recover(Exception, r.json()),
        Exception
    )

    assert recovered_exception.args[0] == "whoops!"


def test_custom_in_middleware():
    """
    Should handle exceptions occured in middleware.
    """
    class C1(HttpController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self):
            return {}

    class M1(HttpMiddleware):
        async def process(
            self,
            request: HttpRequest,
            call_next: HttpNextCall
        ) -> HttpResponse:
            raise Error("whoops!")

    boot: Boot = Boot(
        Module(route="/", Controllers=[C1], Middleware=[M1]),
        ExceptionHandlers={GeneralEh}
    )

    r: TestHttpResponse = boot.app.client.get("/", 401)

    recovered: Error = validation.apply(
        BootProxy.ie().api_indication.recover(Error, r.json()),
        Error
    )

    assert recovered.message == "whoops!"


def test_exception_handled_twice():
    """
    Should raise an error for twice-handled exceptions.
    """
    class Eh1(ExceptionHandler):
        E = Error

    validation.expect(
        Boot,
        ExceptionAlreadyHandledError,
        Module("/", Controllers=[RaiseErrorController]),
        ExceptionHandlers={GeneralEh, Eh1}
    )
