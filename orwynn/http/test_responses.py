import pytest

from orwynn.base import Module
from orwynn.boot import Boot
from orwynn.http import Endpoint, HttpController
from orwynn.http.log.middleware import LogMiddleware
from orwynn.http.responses import RedirectHttpResponse, TestHttpResponse


@pytest.mark.asyncio
async def test_redirect():
    class LocalController(HttpController):
        Route = "/"
        Endpoints = [
            Endpoint(
                method="get"
            )
        ]

        def get(self) -> RedirectHttpResponse:
            return RedirectHttpResponse("https://google.com")


    boot: Boot = await Boot.create(
        Module("/", Controllers=[LocalController]),
        global_middleware={
            LogMiddleware: ["*"]
        }
    )  # type: ignore

    response: TestHttpResponse = boot.app.client.get(
        "/", 307, follow_redirects=False
    )

    assert response.headers.get("location", "") == "https://google.com"
