import pytest
import pytest_asyncio

from orwynn import mongo
from orwynn.base.model.model import Model
from orwynn.base.module.module import Module
from orwynn.boot.boot import Boot
from orwynn.http import Endpoint, EndpointResponse, HttpController
from orwynn.router.errors import (
    UnmatchedEndpointEntityError,
)
from orwynn.utils import validation


@pytest_asyncio.fixture
async def run_endpoint():
    class Item(Model):
        name: str
        price: int

    class Response400(Model):
        message: str
        power: float

    class C1(HttpController):
        Route = "/"
        Endpoints = [
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

    await Boot.create(
        Module(
            route="/",
            Controllers=[C1],
            imports=[mongo.module]
        ),
        apprc={
            "test": {
                "Mongo": {
                    "url": "mongodb://localhost:9006",
                    "database_name": "orwynn_test"
                }
            }
        }
    )


@pytest.mark.asyncio
async def test_not_matched_spec_to_return_type():
    class WrongItem(Model):
        name: str
        doubt: int

    class Item(Model):
        name: str
        price: float

    class C1(HttpController):
        Route = "/"
        Endpoints = [
            Endpoint(
                method="get",
                responses=[EndpointResponse(status_code=200, Entity=WrongItem)]
            )
        ]

        def get(self) -> Item:
            return Item(name="hello", price=1.2)

    await validation.expect_async(
        Boot.create(
            Module(
                route="/",
                Controllers=[C1]
            )
        ),
        UnmatchedEndpointEntityError
    )
