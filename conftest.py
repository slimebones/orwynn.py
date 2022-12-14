"""Main framework-only testing suite.
"""
from pytest import fixture

from orwynn.app.app_mode import AppMode
from orwynn.app.app_service import AppService
from orwynn.base.module.module import Module
from orwynn.boot.boot import Boot
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
def boot(std_struct: Module) -> Boot:
    return Boot(
        mode=AppMode.TEST,
        root_module=std_struct
    )


@fixture
def app(boot: Boot) -> AppService:
    return boot.app
