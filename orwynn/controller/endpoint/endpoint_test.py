from pytest import fixture

from orwynn import validation
from orwynn.boot.Boot import Boot
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.controller.endpoint.EndpointResponse import EndpointResponse
from orwynn.controller.http.HTTPController import HTTPController
from orwynn.model.Model import Model
from orwynn.module.Module import Module
from orwynn.router.UnmatchedEndpointEntityError import (
    UnmatchedEndpointEntityError,
)


@fixture
def run_endpoint():
    class Item(Model):
        name: str
        price: int

    class Response400(Model):
        message: str
        power: float

    class C1(HTTPController):
        ROUTE = "/"
        ENDPOINTS = [
            Endpoint(
                method="get",
                default_status_code=201,
                summary="Best summary",
                tags=["best-item", "buy-now"],
                is_deprecated=True,
                responses=[
                    EndpointResponse(
                        status_code=201,
                        Entity=Item,
                        description="Best response description"
                    ),
                    EndpointResponse(
                        status_code=400,
                        Entity=Response400
                    )
                ]
            )
        ]

        def get(self) -> Item:
            return Item(name="hello", price=1)

    Boot(Module(
        route="/",
        Controllers=[C1]
    ))


def test_not_matched_spec_to_return_type():
    class WrongItem(Model):
        name: str
        doubt: int

    class Item(Model):
        name: str
        price: float

    class C1(HTTPController):
        ROUTE = "/"
        ENDPOINTS = [
            Endpoint(
                method="get",
                responses=[EndpointResponse(status_code=200, Entity=WrongItem)]
            )
        ]

        def get(self) -> Item:
            return Item(name="hello", price=1.2)

    validation.expect(
        Boot,
        UnmatchedEndpointEntityError,
        Module(
            route="/",
            Controllers=[C1]
        )
    )
