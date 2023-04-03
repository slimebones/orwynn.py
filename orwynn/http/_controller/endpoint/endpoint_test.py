from pytest import fixture

from orwynn import mongo
from orwynn.base.model._Model import Model
from orwynn.base.module._Module import Module
from orwynn.boot._Boot import Boot
from orwynn.http import Endpoint, EndpointResponse, HttpController
from orwynn.router.errors import (
    UnmatchedEndpointEntityError,
)
from orwynn.utils import validation


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
            imports=[mongo.module]
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
