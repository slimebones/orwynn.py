from orwynn.util import validation
from orwynn.boot._Boot import Boot
from orwynn.http import Endpoint, HttpController
from orwynn.log.LogMiddleware import LogMiddleware
from orwynn.base.module.Module import Module
from orwynn.http.context._HttpRequestContextId import HttpRequestContextId
from orwynn.context.errors import UndefinedStorageError


def test_basic():
    """Request id should be fetchable from context within request-response
    cycle and unfetchable outside this cycle.
    """
    class C1(HttpController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self) -> dict:
            return {"request_id": HttpRequestContextId().get()}

    boot: Boot = Boot(
        Module(
            "/",
            Controllers=[C1],
            Middleware=[LogMiddleware]
        )
    )

    validation.expect(
        HttpRequestContextId().get,
        UndefinedStorageError
    )

    data: dict = boot.app.client.get_jsonify("/", 200)
    assert type(data["request_id"]) is str and data["request_id"] != ""
