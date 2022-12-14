"""Main framework-only testing suite.
"""
from pytest import fixture

from orwynn.app.app_service import AppService
from orwynn.base.module.module import Module
from orwynn.base.test.http_client import HttpClient
from orwynn.base.test.test_client import TestClient
from orwynn.boot.boot import Boot
from orwynn.boot.boot_mode import BootMode
from orwynn.boot.boot_test import std_boot
from orwynn.di.collecting.collect_modules_test import std_modules
from orwynn.di.collecting.collect_provider_dependencies_test import \
    std_provider_dependencies_map
from orwynn.di.init.init_providers_test import std_di_container
from tests.std import root_module as std_root_module
from tests.structs import (circular_module_struct, long_circular_module_struct,
                           self_importing_module_struct)


@fixture
def std_struct() -> Module:
    # Some predefined configuration for testing
    return std_root_module


@fixture
def std_app(std_boot: Boot) -> AppService:
    return std_boot.app


@fixture
def std_http(std_app: AppService) -> HttpClient:
    return HttpClient(std_app.test_client)
