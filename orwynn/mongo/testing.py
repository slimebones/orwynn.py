import pytest
from orwynn import mongo
from orwynn.base.module.module import Module
from orwynn.boot.boot import Boot
from orwynn.mongo.document import Document


class Item(Document):
    name: str
    price: float
    priority: int = 5


@pytest.fixture
def mongo_boot() -> Boot:
    return Boot(
        Module(route="/", imports=[mongo.module]),
        apprc={
            "prod": {
                "Mongo": {
                    "database_name": "orwynn-test"
                }
            }
        }
    )


@pytest.fixture
def document_1(mongo_boot) -> Item:
    return Item(
        name="pizza",
        price=1.2,
        priority=2
    ).create()


@pytest.fixture
def document_2(mongo_boot) -> Item:
    return Item(
        name="donut",
        price=1
    ).create()
