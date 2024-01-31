import os

import pytest_asyncio
from fcode import FcodeCore

from orwynn.app import App
from orwynn.boot import Boot
from orwynn.sys import Sys
from orwynn.tst import Client


@pytest_asyncio.fixture(autouse=True)
async def autorun():
    os.environ["ORWYNN_DEBUG"] = "1"

    yield

    # discard fcode separately since it uses custom singleton to avoid
    # circular deps
    FcodeCore.discard(should_validate=False)
    for sys_type in Sys.__subclasses__():
        await sys_type._internal_destroy()  # noqa: SLF001

@pytest_asyncio.fixture
async def app() -> App:
    return await Boot.get_app()

@pytest_asyncio.fixture
async def client(app: App, aiohttp_client):
    return Client(await aiohttp_client(app))

