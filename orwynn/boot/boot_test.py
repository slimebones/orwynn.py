from pytest import fixture
from orwynn.boot.boot_mode import BootMode
from orwynn.base.module import Module

from orwynn.boot import Boot


@fixture
def std_boot(std_struct: Module):
    yield Boot(
        mode=BootMode.TEST,
        root_module=std_struct
    )
    Boot.discard()


def test_init_mode_test(std_struct: Module):
    Boot(
        mode=BootMode.TEST,
        root_module=std_struct
    )


def test_init_mode_dev(std_struct: Module):
    Boot(
        mode=BootMode.DEV,
        root_module=std_struct
    )


def test_init_mode_prod(std_struct: Module):
    Boot(
        mode=BootMode.PROD,
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
