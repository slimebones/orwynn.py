from pytest import fixture

from orwynn.app.app_mode_enum import AppModeEnum
from orwynn.app.app_service import AppService
from orwynn.base.module.root_module import RootModule
from orwynn.base.test.test_client import TestClient
from orwynn.boot.boot import Boot
from tests.std import root_module as std_root_module


@fixture
def root_module() -> RootModule:
    # Some predefined configuration for testing
    return std_root_module


@fixture
def boot(root_module: RootModule) -> Boot:
    return Boot(
        mode=AppModeEnum.TEST,
        root_module=root_module
    )

@fixture
def app(boot: Boot) -> AppService:
    return boot.app