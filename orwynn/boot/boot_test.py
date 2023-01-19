import os

from pytest import fixture

from orwynn import validation
from orwynn.apprc.AppRC import AppRC
from orwynn.boot.Boot import Boot
from orwynn.boot.BootMode import BootMode
from orwynn.di.DI import DI
from orwynn.module.Module import Module
from orwynn.mongo.Mongo import Mongo
from orwynn.proxy.BootProxy import BootProxy
from tests.std.text import TextConfig


@fixture
def std_boot(std_struct: Module) -> Boot:
    return Boot(
        root_module=std_struct
    )


@fixture
def run_std(std_struct: Module):
    Boot(std_struct)


@fixture
def std_mongo_boot(std_struct: Module) -> Boot:
    return Boot(
        root_module=std_struct
    )


@fixture
def set_prod_mode():
    os.environ["Orwynn_Mode"] = "prod"


@fixture
def set_dev_mode():
    os.environ["Orwynn_Mode"] = "dev"


@fixture
def set_test_mode():
    os.environ["Orwynn_Mode"] = "test"


@fixture
def set_std_apprc_path_env() -> None:
    os.environ["Orwynn_AppRCPath"] = os.path.join(
        os.getcwd(),
        "tests/std/apprc.yml"
    )


def test_init_mode_default(std_struct: Module):
    os.environ["Orwynn_Mode"] = ""
    boot: Boot = Boot(
        root_module=std_struct
    )
    assert boot.mode == BootMode.DEV


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


def test_init_incorrect_mode(std_struct: Module):
    os.environ["Orwynn_Mode"] = "helloworld"
    validation.expect(Boot, ValueError, root_module=std_struct)


def test_init_enable_mongo(std_struct: Module, set_std_apprc_path_env):
    Boot(
        root_module=std_struct
    )

    validation.validate(DI.ie().find("Mongo"), Mongo)


def test_nested_configs_prod(
    std_struct: Module,
    set_std_apprc_path_env,
    set_prod_mode
):
    Boot(
        root_module=std_struct
    )
    app_rc: AppRC = BootProxy.ie().apprc
    text_config: TextConfig = DI.ie().find("TextConfig")

    assert app_rc["Text"]["words_amount"] == text_config.words_amount == 1


def test_nested_configs_dev(
    std_struct: Module,
    set_std_apprc_path_env,
    set_dev_mode
):
    Boot(
        root_module=std_struct
    )
    app_rc: AppRC = BootProxy.ie().apprc
    text_config: TextConfig = DI.ie().find("TextConfig")

    assert app_rc["Text"]["words_amount"] == text_config.words_amount == 2


def test_nested_configs_test(
    std_struct: Module,
    set_std_apprc_path_env,
    set_test_mode
):
    Boot(
        root_module=std_struct
    )
    app_rc: AppRC = BootProxy.ie().apprc
    text_config: TextConfig = DI.ie().find("TextConfig")

    assert app_rc["Text"]["words_amount"] == text_config.words_amount == 3
