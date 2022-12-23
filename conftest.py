"""Main framework-only testing suite.
"""
import os

from pytest import fixture

from orwynn.app.app_test import std_app
from orwynn.app.AppService import AppService
from orwynn.base.module.Module import Module
from orwynn.base.test.HttpClient import HttpClient
from orwynn.base.test.TestClient import TestClient
from orwynn.base.worker._Worker import Worker
from orwynn.boot.Boot import Boot
from orwynn.proxy.boot_data_proxy_test import std_boot_data_proxy
from orwynn.boot.boot_test import run_std, std_boot, std_mongo_boot
from orwynn.boot.BootMode import BootMode
from orwynn.di.collecting.collect_modules_test import std_modules
from orwynn.di.collecting.collect_provider_dependencies_test import \
    std_provider_dependencies_map
from orwynn.di.di_test import std_di_container
from orwynn.mongo.Mongo import Mongo
from orwynn.util.web.http_test import std_http
from tests.structs import (circular_module_struct, long_circular_module_struct,
                           self_importing_module_struct, std_struct)

@fixture(autouse=True)
def run_around_tests():
    yield
    try:
        Mongo.ie().drop_database()
    except TypeError:
        # Mongo is not initialized, skip
        pass
    __discard_workers()


def __discard_workers(W: type[Worker] = Worker):
    for NestedW in W.__subclasses__():
        __discard_workers(NestedW)
    W.discard(should_validate=False)
    os.environ["Orwynn_Mode"] = ""
    os.environ["Orwynn_RootDir"] = ""
    os.environ["Orwynn_AppRcDir"] = ""
