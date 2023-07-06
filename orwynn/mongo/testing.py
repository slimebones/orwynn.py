import pytest

from orwynn import mongo
from orwynn.base.module.module import Module
from orwynn.boot.boot import Boot


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
