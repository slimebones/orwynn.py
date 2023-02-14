from orwynn import validation, web
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.controller.http.HttpController import HttpController
from orwynn.middleware.HttpMiddleware import HttpMiddleware
from orwynn.middleware.HttpNextCallFn import HttpNextCallFn
from orwynn.module.Module import Module


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
            self, request: web.Request, call_next: HttpNextCallFn
        ) -> web.Response:
            return await super().process(request, call_next)

    validation.expect(
        Module,
        ValueError,
        route=None,
        Middleware=[M1]
    )
