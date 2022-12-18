"""Main framework-only testing suite.
"""
from pytest import fixture

from orwynn.app.app_test import std_app
from orwynn.app.AppService import AppService
from orwynn.base.module.Module import Module
from orwynn.base.test.HttpClient import HttpClient
from orwynn.base.test.TestClient import TestClient
from orwynn.base.worker.Worker import Worker
from orwynn.boot.Boot import Boot
from orwynn.boot.boot_data_proxy_test import std_boot_data_proxy
from orwynn.boot.boot_mode import BootMode
from orwynn.boot.boot_test import std_boot
from orwynn.di.collecting.collect_modules_test import std_modules
from orwynn.di.collecting.collect_provider_dependencies_test import \
    std_provider_dependencies_map
from orwynn.di.di_test import std_di_container
from orwynn.util.http.http_test import std_http
from tests.structs import (circular_module_struct, long_circular_module_struct,
                           self_importing_module_struct, std_struct)


@fixture(autouse=True)
def run_around_tests():
    yield
    __discard_workers()


def __discard_workers(W: type[Worker] = Worker):
    for NestedW in W.__subclasses__():
        __discard_workers(NestedW)
    W.discard(should_validate=False)
