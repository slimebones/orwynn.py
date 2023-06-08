"""Main framework-only testing suite.
"""
import contextlib
import os

from pytest import fixture

from orwynn.di.collecting.test_modules import std_modules
from orwynn.di.collecting.test_provider_dependencies import (
    std_provider_dependencies_map,
)
from orwynn.di.di import Di
from orwynn.di.testing import std_di_container
from orwynn.di.errors import MissingDiObjectError
from orwynn.app import AppMode
from orwynn.app.app import App
from orwynn.app.test_main import std_app
from orwynn.base.module.module import Module
from orwynn.base.worker.worker import Worker
from orwynn.boot.boot import Boot
from orwynn.boot.test_main import (
    run_std,
    set_std_apprc_path_env,
    std_boot,
    std_mongo_boot,
)
from orwynn.helpers.ENVIRONS import ENVIRONS
from orwynn.http._controller.endpoint.endpoint_test import run_endpoint
from orwynn.http.testing import std_http
from orwynn.log.log_test import log_apprc_sink_to_writer, writer
from orwynn.mongo._Mongo import Mongo
from orwynn.testing._Client import Client
from orwynn.testing._EmbeddedTestClient import EmbeddedTestClient
from orwynn.utils import validation
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
