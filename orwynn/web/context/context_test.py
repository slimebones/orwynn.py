from orwynn import validation
from orwynn.boot.Boot import Boot
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.controller.http.HTTPController import HTTPController
from orwynn.log import module as log_module
from orwynn.log.LogMiddleware import LogMiddleware
from orwynn.module.Module import Module
from orwynn.web.context.RequestContextId import RequestContextId
from orwynn.web.context.UndefinedStorageError import UndefinedStorageError


def test_basic():
    """Request id should be fetchable from context within request-response
    cycle and unfetchable outside this cycle.
    """
    class C1(HTTPController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self) -> dict:
            return {"request_id": RequestContextId().get()}

    boot: Boot = Boot(
        Module(
            "/",
            Controllers=[C1],
            Middleware=[LogMiddleware],
            imports=[log_module]
        )
    )

    validation.expect(
        RequestContextId().get,
        UndefinedStorageError
    )

    data: dict = boot.app.client.get_jsonify("/", 200)
    assert type(data["request_id"]) is str and data["request_id"] != ""
