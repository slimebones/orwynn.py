from pytest import fixture
from orwynn.app.app_mode_enum import AppModeEnum
from orwynn.base.module.root_module import RootModule

from orwynn.boot.boot import Boot


def test_init_mode_test(root_module: RootModule):
    Boot(
        mode=AppModeEnum.TEST,
        root_module=root_module
    )


def test_init_mode_dev(root_module: RootModule):
    Boot(
        mode=AppModeEnum.DEV,
        root_module=root_module
    )


def test_init_mode_prod(root_module: RootModule):
    Boot(
        mode=AppModeEnum.PROD,
        root_module=root_module
    )


def test_init_mode_test_str(root_module: RootModule):
    Boot(
        mode="test",
        root_module=root_module
    )


def test_init_mode_dev_str(root_module: RootModule):
    Boot(
        mode="dev",
        root_module=root_module
    )


def test_init_mode_prod_str(root_module: RootModule):
    Boot(
        mode="prod",
        root_module=root_module
    )

