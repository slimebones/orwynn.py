import os

import pytest_asyncio
from pykit.fcode import FcodeCore
from rxcat import ServerBus

from orwynn import App
from orwynn.mongo import Mongo
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
    await ServerBus.destroy()
    await Mongo.destroy()

@pytest_asyncio.fixture
async def app() -> App:
    app = await App.create_app()
    return app

@pytest_asyncio.fixture
async def client(app: App, aiohttp_client):
    return Client(await aiohttp_client(app))

