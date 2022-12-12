from orwynn.app.app_mode_enum import AppModeEnum
from orwynn.base.module.module import Module

from orwynn.boot.boot import Boot


def test_init_mode_test(std_struct: Module):
    Boot(
        mode=AppModeEnum.TEST,
        root_module=std_struct
    )


def test_init_mode_dev(std_struct: Module):
    Boot(
        mode=AppModeEnum.DEV,
        root_module=std_struct
    )


def test_init_mode_prod(std_struct: Module):
    Boot(
        mode=AppModeEnum.PROD,
        root_module=std_struct
    )


def test_init_mode_test_str(std_struct: Module):
    Boot(
        mode="test",
        root_module=std_struct
    )


def test_init_mode_dev_str(std_struct: Module):
    Boot(
        mode="dev",
        root_module=std_struct
    )


def test_init_mode_prod_str(std_struct: Module):
    Boot(
        mode="prod",
        root_module=std_struct
    )
