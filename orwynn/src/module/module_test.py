from orwynn import validation
from orwynn.src.controller.endpoint.Endpoint import Endpoint
from orwynn.src.controller.http.HttpController import HttpController
from orwynn.src.middleware.HttpMiddleware import HttpMiddleware
from orwynn.src.middleware.HttpNextCall import HttpNextCall
from orwynn.src.module.Module import Module
from orwynn.src.web.http.requests import HttpRequest
from orwynn.src.web.http.responses import HttpResponse


def test_controller_added_to_no_route():
    class C1(HttpController):
        ROUTE = "/"
        ENDPOINTS = [
            Endpoint(
                method="get"
            )
        ]

        def get(self, *args, **kwargs) -> dict:
            return {}

    validation.expect(
        Module,
        ValueError,
        route=None,
        Controllers=[C1]
    )


def test_middleware_added_to_no_route():
    class M1(HttpMiddleware):
        async def process(
            self, request: HttpRequest, call_next: HttpNextCall
        ) -> HttpResponse:
            return await super().process(request, call_next)

    validation.expect(
        Module,
        ValueError,
        route=None,
        Middleware=[M1]
    )
