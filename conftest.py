"""Main framework-only testing suite.

Word "struct" used to refer to root module for the sake of descriptiveness -
e.g. for fixtures like "self_importing_struct" to annotate that this root
module has been built with some modules using self importing.
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


@fixture
def std_struct() -> Module:
    # Some predefined configuration for testing
    return std_root_module


@fixture
def boot(std_struct: Module) -> Boot:
    return Boot(
        mode=AppMode.TEST,
        root_module=std_struct,
        FrameworkServices=[AppService]
    )


@fixture
def app(boot: Boot) -> AppService:
    return boot.app
