from orwynn.base.module.module import Module
from orwynn.http import (
    Endpoint,
    HttpController,
    HttpMiddleware,
    HttpNextCall,
    HttpRequest,
    HttpResponse,
)
from orwynn.utils import validation


def test_controller_added_to_no_route():
    class C1(HttpController):
        Route = "/"
        Endpoints = [
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
