from pytest import fixture

from orwynn import validation
from orwynn.src.boot.Boot import Boot
from orwynn.src.controller.endpoint.Endpoint import Endpoint
from orwynn.src.controller.endpoint.EndpointResponse import EndpointResponse
from orwynn.src.controller.http.HttpController import HttpController
from orwynn.src.model.Model import Model
from orwynn.src.module.Module import Module
from orwynn.src.mongo import module
from orwynn.src.router.UnmatchedEndpointEntityError import (
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

    class C1(HttpController):
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

    Boot(
        Module(
            route="/",
            Controllers=[C1],
            imports=[module.module]
        ),
        apprc={
            "test": {
                "Mongo": {
                    "database_name": "orwynn-test"
                }
            }
        }
    )


def test_not_matched_spec_to_return_type():
    class WrongItem(Model):
        name: str
        doubt: int

    class Item(Model):
        name: str
        price: float

    class C1(HttpController):
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
