from orwynn import validation, web
from orwynn.app.ErrorHandler import ErrorHandler
from orwynn.boot.Boot import Boot
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.controller.http.HTTPController import HTTPController
from orwynn.error.Error import Error
from orwynn.module.Module import Module
from orwynn.proxy.BootProxy import BootProxy
from orwynn.service.Service import Service
from orwynn.test.Client import Client
from orwynn.web import JSONResponse, Request, TestResponse


def test_basic():
    class C1(HTTPController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self):
            raise Error("whoops!")

    class EH1(ErrorHandler):
        E = Error

        def handle(self, request: Request, error: Error):
            return JSONResponse(error.api, 400)

    boot: Boot = Boot(
        Module(route="/", Controllers=[C1]),
        ErrorHandlers=[EH1]
    )
    http: Client = boot.app.client

    r: TestResponse = http.get("/", 400)

    recovered_error: Error = validation.apply(
        BootProxy.ie().api_indication.recover(Error, r.json()),
        Error
    )

    assert recovered_error.message == "whoops!"


def test_default_exception():
    class C1(HTTPController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self):
            raise TypeError("whoops!")

    boot: Boot = Boot(
        Module(route="/", Controllers=[C1])
    )
    http: Client = boot.app.client

    r: TestResponse = http.get("/", 400)

    recovered_exception: Exception = validation.apply(
        BootProxy.ie().api_indication.recover(Exception, r.json()),
        Exception
    )

    assert recovered_exception.args[0] == "whoops!"


def test_identical_error_handlers():
    # Last added error handler should only be executed for the error
    #
    class C1(HTTPController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self):
            raise Error("whoops!")

    class EH1(ErrorHandler):
        E = Error

        def handle(self, request: Request, error: Error):
            return JSONResponse(error.api, 400)

    class EH2(ErrorHandler):
        E = Error

        def handle(self, request: Request, error: Error):
            return JSONResponse(error.api, 401)

    boot: Boot = Boot(
        Module(route="/", Controllers=[C1]),
        # Order matters
        ErrorHandlers=[EH1, EH2]
    )
    http: Client = boot.app.client

    r: TestResponse = http.get("/", 401)

    recovered_error: Error = validation.apply(
        BootProxy.ie().api_indication.recover(Error, r.json()),
        Error
    )

    assert recovered_error.message == "whoops!"


def test_as_acceptor():
    # Tests if an error handler can truly accept Providers
    #
    ASSERTED_TEXT: str = "Hello, world!"

    class CoolService(Service):
        def do_something(
            self
        ) -> str:
            return ASSERTED_TEXT

    class C1(HTTPController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self):
            raise Error("whoops!")

    class EH1(ErrorHandler):
        E = Error

        def __init__(self, cool_service: CoolService) -> None:
            self.__cool_service: CoolService = cool_service

        def handle(self, request: Request, error: Error) -> web.Response:
            data: dict = error.api
            data["__test_meta_info"] = self.__cool_service.do_something()
            return JSONResponse(data, 400)

    boot: Boot = Boot(
        Module(route="/", Providers=[CoolService], Controllers=[C1]),
        # Order matters
        ErrorHandlers=[EH1]
    )
    client: Client = boot.app.client

    data: dict = client.get_jsonify("/", 400)

    assert data["__test_meta_info"] == ASSERTED_TEXT
