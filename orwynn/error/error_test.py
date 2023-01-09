from orwynn.boot.Boot import Boot
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.controller.http.HTTPController import HTTPController
from orwynn.error.Error import Error
from orwynn.module.Module import Module


def test_custom_status_code():
    class C1(HTTPController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self):
            raise Error("whoops!", status_code=401)

    boot: Boot = Boot(
        Module(route="/", Controllers=[C1])
    )

    boot.app.client.get("/", 401)
