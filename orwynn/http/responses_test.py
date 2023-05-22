from orwynn.base import Module
from orwynn.boot import Boot
from orwynn.http import HttpController, Endpoint

from orwynn.http._responses import RedirectHttpResponse, TestHttpResponse


def test_redirect():
    class LocalController(HttpController):
        ROUTE = "/"
        ENDPOINTS = [
            Endpoint(
                method="get"
            )
        ]

        def get(self) -> RedirectHttpResponse:
            return RedirectHttpResponse("https://google.com")


    boot: Boot = Boot(
        Module("/", Controllers=[LocalController])
    )  # type: ignore

    response: TestHttpResponse = boot.app.client.get("/", 307)

    print(response.headers)

    assert 0, "OK"
