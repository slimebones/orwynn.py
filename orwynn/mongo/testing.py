import pytest_asyncio

from orwynn import mongo
from orwynn.base.module.module import Module
from orwynn.boot.boot import Boot


@pytest_asyncio.fixture
async def mongo_boot() -> Boot:
    return await Boot.create(
        Module(route="/", imports=[mongo.module]),
        apprc={
            "prod": {
                "Mongo": {
                    "url": "mongodb://localhost:9006",
                    "database_name": "orwynn-test"
                }
            }
        }
    )
