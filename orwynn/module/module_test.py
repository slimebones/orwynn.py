from orwynn import validation
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.controller.http.HttpController import HttpController
from orwynn.middleware.HttpMiddleware import HttpMiddleware
from orwynn.middleware.HttpNextCall import HttpNextCall
from orwynn.module.Module import Module
from orwynn.web.http.requests import HttpRequest
from orwynn.web.http.responses import HttpResponse


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
