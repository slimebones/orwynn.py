import os

import pytest_asyncio
from fcode import FcodeCore
from rxcat import Bus

from orwynn.app import App
from orwynn.boot import Boot
from orwynn.mongo import MongoUtils
from orwynn.sys import Sys
from orwynn.tst import Client


@pytest_asyncio.fixture(autouse=True)
async def autorun():
    os.environ["ORWYNN_MODE"] = "test"
    os.environ["ORWYNN_DEBUG"] = "1"
    os.environ["ORWYNN_ALLOW_CLEAN"] = "1"

    yield

    for sys_type in Sys.__subclasses__():
        await sys_type._internal_destroy()  # noqa: SLF001

    FcodeCore.deflock = False
    FcodeCore.clean_non_decorator_codes()
    await Bus.destroy()
    await MongoUtils.destroy()

@pytest_asyncio.fixture
async def app() -> App:
    app = await Boot.create_app()
    return app

@pytest_asyncio.fixture
async def client(app: App, aiohttp_client):
    return Client(await aiohttp_client(app))

