import os

import pytest
from pytest import fixture

from orwynn import validation
from orwynn.apprc.AppRC import AppRC
from orwynn.boot.Boot import Boot
from orwynn.boot.BootMode import BootMode
from orwynn.controller.endpoint.Endpoint import Endpoint
from orwynn.controller.http.HttpController import HttpController
from orwynn.di.circular_dependency_error import CircularDependencyError
from orwynn.di.Di import Di
from orwynn.module.Module import Module
from orwynn.mongo.Mongo import Mongo
from orwynn.proxy.BootProxy import BootProxy
from orwynn.service.Service import Service
from tests.std.text import TextConfig


class _GService(Service):
    def calculate(self, *args: int) -> int:
        return sum(args)


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

    validation.validate(Di.ie().find("Mongo"), Mongo)


def test_nested_configs_prod(
    std_struct: Module,
    set_std_apprc_path_env,
    set_prod_mode
):
    Boot(
        root_module=std_struct
    )
    app_rc: AppRC = BootProxy.ie().apprc
    text_config: TextConfig = Di.ie().find("TextConfig")

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
    text_config: TextConfig = Di.ie().find("TextConfig")

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
    text_config: TextConfig = Di.ie().find("TextConfig")

    assert app_rc["Text"]["words_amount"] == text_config.words_amount == 3


def test_global_route():
    class C(HttpController):
        ROUTE = "/message"
        ENDPOINTS = [Endpoint(method="get")]

        def get(self) -> dict:
            return {"message": "hello"}

    boot: Boot = Boot(
        root_module=Module("/user", Controllers=[C]),
        global_route="/donuts"
    )

    boot.app.client.get_jsonify("/donuts/user/message", 200)


@pytest.fixture
def __gmodule() -> Module:
    return Module(
        "/gmodule",
        Providers=[_GService],
        exports=[_GService]
    )

def test_global_modules(
    __gmodule: Module
):
    class C1(HttpController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

        def __init__(self, gservice: _GService) -> None:
            super().__init__()
            self.__gservice: _GService = gservice

        def get(self) -> dict:
            return {"value": self.__gservice.calculate(1, 2, 3)}

    boot: Boot = Boot(
        root_module=Module("/", Controllers=[C1]),
        global_modules=[__gmodule]
    )

    data: dict = boot.app.client.get_jsonify("/", 200)

    assert data["value"] == 6


def test_global_modules_reimported(
    __gmodule: Module
):
    """No module can import globally-defined modules."""
    class C1(HttpController):
        ROUTE = "/"
        ENDPOINTS = [Endpoint(method="get")]

        def __init__(self, gservice: _GService) -> None:
            super().__init__()
            self.__gservice: _GService = gservice

        def get(self) -> dict:
            return {"value": self.__gservice.calculate(1, 2, 3)}

    validation.expect(
        Boot,
        CircularDependencyError,
        # Root module reimports globally defined module
        root_module=Module("/", Controllers=[C1], imports=[__gmodule]),
        global_modules=[__gmodule]
    )
