import os
from pytest import fixture
from orwynn.boot.BootMode import BootMode
from orwynn.base.module.Module import Module

from orwynn.boot.Boot import Boot


@fixture
def std_boot(std_struct: Module) -> Boot:
    return Boot(
        root_module=std_struct
    )


def test_init_mode_test(std_struct: Module):
    os.environ["Orwynn_Mode"] = "test"
    boot: Boot = Boot(
        root_module=std_struct
    )
    assert boot.mode == BootMode.TEST


def test_init_mode_dev(std_struct: Module):
    os.environ["Orwynn_Mode"] = "dev"
    boot: Boot = Boot(
        root_module=std_struct
    )
    assert boot.mode == BootMode.DEV


def test_init_mode_prod(std_struct: Module):
    os.environ["Orwynn_Mode"] = "prod"
    boot: Boot = Boot(
        root_module=std_struct
    )
    assert boot.mode == BootMode.PROD
