from pytest import fixture
from orwynn import app

from orwynn.app._AppService import AppService
from orwynn.base.controller.Controller import Controller
from orwynn.base.error.Error import Error
from orwynn.base.module.Module import Module
from orwynn.base.test.HttpClient import HttpClient
from orwynn.boot.Boot import Boot
from orwynn.util import validation
from orwynn.util.web import JSONResponse, Request, Response, TestResponse


@fixture
def std_app(std_boot: Boot) -> AppService:
    return std_boot.app


def test_error_handler():
    class C1(Controller):
        ROUTE = "/"
        METHODS = ["get"]

        def get(self):
            raise ValueError("wow")
            # raise Error("whoops!")

    def handle_error(request: Request, error: Error):
        return JSONResponse({"message": "error"}, 400)

    boot: Boot = Boot(
        Module(route="/", Controllers=[C1]),
        error_handlers=[app.ErrorHandler(E=Error, handler=handle_error)]
    )
    http: HttpClient = boot.app.http_client

    r: TestResponse = http.get("/", 400)
    print(r.json())
    assert False
