from orwynn.app.app_mode_enum import AppModeEnum
from orwynn.base.module.root_module import RootModule

from orwynn.boot.boot import Boot


def test_init_mode_test(std_structure: RootModule):
    Boot(
        mode=AppModeEnum.TEST,
        root_module=std_structure
    )


def test_init_mode_dev(std_structure: RootModule):
    Boot(
        mode=AppModeEnum.DEV,
        root_module=std_structure
    )


def test_init_mode_prod(std_structure: RootModule):
    Boot(
        mode=AppModeEnum.PROD,
        root_module=std_structure
    )


def test_init_mode_test_str(std_structure: RootModule):
    Boot(
        mode="test",
        root_module=std_structure
    )


def test_init_mode_dev_str(std_structure: RootModule):
    Boot(
        mode="dev",
        root_module=std_structure
    )


def test_init_mode_prod_str(std_structure: RootModule):
    Boot(
        mode="prod",
        root_module=std_structure
    )
