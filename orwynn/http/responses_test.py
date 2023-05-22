from orwynn.base import Module
from orwynn.boot import Boot
from orwynn.http import Endpoint, HttpController
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

    response: TestHttpResponse = boot.app.client.get(
        "/", 307, follow_redirects=False
    )

    assert response.headers.get("location", "") =="https://google.com"
