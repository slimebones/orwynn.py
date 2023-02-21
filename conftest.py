"""Main framework-only testing suite.
"""
import contextlib
import os

from pytest import fixture

from orwynn.src import validation
from orwynn.src.app.App import App
from orwynn.src.app.app_test import std_app
from orwynn.src.boot.Boot import Boot
from orwynn.src.boot.boot_test import (
    run_std,
    set_std_apprc_path_env,
    std_boot,
    std_mongo_boot,
)
from orwynn.src.boot.BootMode import BootMode
from orwynn.src.controller.endpoint.endpoint_test import run_endpoint
from orwynn.src.di.collecting.collect_modules_test import std_modules
from orwynn.src.di.collecting.collect_provider_dependencies_test import (
    std_provider_dependencies_map,
)
from orwynn.src.di.Di import Di
from orwynn.src.di.di_test import std_di_container
from orwynn.src.di.MissingDiObjectError import MissingDiObjectError
from orwynn.src.log.log_test import log_apprc_sink_to_writer, writer
from orwynn.src.module.Module import Module
from orwynn.src.mongo.Mongo import Mongo
from orwynn.src.proxy.boot_data_proxy_test import std_boot_data_proxy
from orwynn.src.testing.Client import Client
from orwynn.src.testing.EmbeddedTestClient import EmbeddedTestClient
from orwynn.src.web.http.http_test import std_http
from orwynn.src.worker.Worker import Worker
from tests.structs import (
    circular_module_struct,
    long_circular_module_struct,
    self_importing_module_struct,
    std_struct,
)


@fixture(autouse=True)
def run_around_tests():
    os.environ["Orwynn_Mode"] = "test"

    yield

    # Suppress:
    #   MissingDIObjectError: Mongo is not initialized, skip
    #   TypeError: DI wasn't initialized, skip
    with contextlib.suppress(MissingDiObjectError, TypeError):
        validation.apply(Di.ie().find("Mongo"), Mongo).drop_database()
    __discardWorkers()


def __discardWorkers(W: type[Worker] = Worker):
    for NestedW in W.__subclasses__():
        __discardWorkers(NestedW)
    W.discard(should_validate=False)
    os.environ["Orwynn_Mode"] = ""
    os.environ["Orwynn_RootDir"] = ""
    os.environ["Orwynn_AppRcPath"] = ""
