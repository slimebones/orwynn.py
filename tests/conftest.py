import pytest_asyncio

from orwynn.app import App
from orwynn.boot import Boot

@pytest_asyncio.fixture
async def app() -> App:
    return await Boot.get_app()

@pytest_asyncio.fixture
async def client(app: App, aiohttp_client):
    return await aiohttp_client(app)

