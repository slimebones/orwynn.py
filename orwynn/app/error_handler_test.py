from orwynn.app.ErrorHandler import ErrorHandler
from orwynn.boot.Boot import Boot
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.controller.http.HTTPController import HTTPController
from orwynn.error.Error import Error
from orwynn.module.Module import Module
from orwynn.proxy.BootProxy import BootProxy
from orwynn.test.HttpClient import HttpClient
from orwynn.util import validation
from orwynn.util.web import JSONResponse, Request, TestResponse


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
    http: HttpClient = boot.app.http_client

    r: TestResponse = http.get("/", 400)

    recovered_error: Error = validation.apply(
        BootProxy.ie().api_indication.recover(r.json()),
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
    http: HttpClient = boot.app.http_client

    r: TestResponse = http.get("/", 400)

    recovered_exception: Exception = validation.apply(
        BootProxy.ie().api_indication.recover(r.json()),
        Exception
    )

    assert recovered_exception.args[0] == "whoops!"


def test_identical_error_handlers():
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
    http: HttpClient = boot.app.http_client

    r: TestResponse = http.get("/", 401)

    recovered_error: Error = validation.apply(
        BootProxy.ie().api_indication.recover(r.json()),
        Error
    )

    assert recovered_error.message == "whoops!"
