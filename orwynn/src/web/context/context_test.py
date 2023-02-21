from orwynn.src import validation
from orwynn.src.boot.Boot import Boot
from orwynn.src.controller.endpoint.Endpoint import Endpoint
from orwynn.src.controller.http.HttpController import HttpController
from orwynn.src.log.LogMiddleware import LogMiddleware
from orwynn.src.module.Module import Module
from orwynn.src.web.context.RequestContextId import RequestContextId
from orwynn.src.web.context.UndefinedStorageError import UndefinedStorageError


def test_basic():
    """Request id should be fetchable from context within request-response
    cycle and unfetchable outside this cycle.
    """
    class C1(HttpController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self) -> dict:
            return {"request_id": RequestContextId().get()}

    boot: Boot = Boot(
        Module(
            "/",
            Controllers=[C1],
            Middleware=[LogMiddleware]
        )
    )

    validation.expect(
        RequestContextId().get,
        UndefinedStorageError
    )

    data: dict = boot.app.client.get_jsonify("/", 200)
    assert type(data["request_id"]) is str and data["request_id"] != ""
