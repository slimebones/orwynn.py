"""Main framework testing suite.

Word "structure" used to refer to RootModule for the sake of descriptiveness -
e.g. for fixtures like "self_importing_structure" to annotate that this root
module has been built with some modules using self importing.
"""
from pytest import fixture

from orwynn.app.app_mode_enum import AppModeEnum
from orwynn.app.app_service import AppService
from orwynn.base.module.root_module import RootModule
from orwynn.boot.boot import Boot
from tests.std import root_module as std_root_module


@fixture
def std_structure() -> RootModule:
    # Some predefined configuration for testing
    return std_root_module


@fixture
def boot(std_structure: RootModule) -> Boot:
    return Boot(
        mode=AppModeEnum.TEST,
        root_module=std_structure
    )


@fixture
def app(boot: Boot) -> AppService:
    return boot.app
