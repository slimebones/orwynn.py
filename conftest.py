"""Main framework-only testing suite.
"""
import contextlib
import os

import pytest_asyncio
from pykit import validation
from pytest import fixture

from orwynn import sql
from orwynn.app import AppMode
from orwynn.app.app import App
from orwynn.app.test_main import std_app
from orwynn.boot.boot import Boot
from orwynn.boot.test_main import (
    run_std,
    set_std_apprc_path_env,
    std_boot,
    std_mongo_boot,
)
from orwynn.bootscript.bootscript import Bootscript
from orwynn.di.collecting.providerdependencies.test_main import (
    std_provider_dependencies_map,
)
from orwynn.di.collecting.test_modules import std_modules
from orwynn.di.di import Di
from orwynn.di.errors import MissingDiObjectError
from orwynn.di.testing import std_di_container
from orwynn.helpers.constants import ENVIRONS
from orwynn.http.controller.endpoint.test_main import run_endpoint
from orwynn.http.testing import std_http
from orwynn.log.test_main import log_apprc_sink_to_writer, writer
from orwynn.module.module import Module
from orwynn.mongo.document.testing import (
    document_1,
    document_2,
    nested_document_1,
)
from orwynn.mongo.mongo import Mongo
from orwynn.mongo.testing import mongo_boot
from orwynn.sql.testing import create_tables_bootscript, s1_table_search
from orwynn.testing.client import Client
from orwynn.testing.embeddedclient import EmbeddedTestClient
from orwynn.worker.worker import Worker
from tests.structs import (
    circular_module_struct,
    long_circular_module_struct,
    self_importing_module_struct,
    std_struct,
)


@fixture(autouse=True)
def run_around_tests():
    os.environ["ORWYNN_MODE"] = "test"

    yield

    # Suppress:
    #   MissingDIObjectError: Mongo is not initialized, skip
    #   TypeError: DI wasn't initialized, skip
    with contextlib.suppress(MissingDiObjectError, TypeError):
        validation.apply(Di.ie().find("Mongo"), Mongo).drop_database()
    _discardWorkers()


def _discardWorkers(W: type[Worker] = Worker):
    for NestedW in W.__subclasses__():
        _discardWorkers(NestedW)
    W.discard(should_validate=False)

    _delete_environs()


def _delete_environs():
    for environ in ENVIRONS:
        with contextlib.suppress(KeyError):
            del os.environ[environ]

@pytest_asyncio.fixture
async def bare_boot(create_tables_bootscript: Bootscript) -> Boot:
    return await Boot.create(Module(
        imports=[sql.module]),
        bootscripts=[create_tables_bootscript],
        apprc={
            "prod": {
                "SQL": {
                    "database_kind": "sqlite",
                    "database_path": ":memory:"
                }
            }
        }
    )
