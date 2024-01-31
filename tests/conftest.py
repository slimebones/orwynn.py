import pytest_asyncio

from orwynn.app import App
from orwynn.boot import Boot
from orwynn.tst import Client

@pytest_asyncio.fixture
async def app() -> App:
    return await Boot.get_app()

@pytest_asyncio.fixture
async def client(app: App, aiohttp_client):
    return Client(await aiohttp_client(app))

