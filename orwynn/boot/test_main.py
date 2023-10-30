import os

import pytest
import pytest_asyncio

from orwynn.app import AppMode
from orwynn.apprc.apprc import AppRc
from orwynn.base.module.errors import CircularDependencyError
from orwynn.base.module.module import Module
from orwynn.base.service.service import Service
from orwynn.boot.boot import Boot
from orwynn.di.di import Di
from orwynn.http import Endpoint, HttpController
from orwynn.mongo.mongo import Mongo
from orwynn.proxy.boot import BootProxy
from orwynn.utils import validation
from tests.std.text import TextConfig


class _GService(Service):
    def calculate(self, *args: int) -> int:
        return sum(args)


@pytest_asyncio.fixture
async def std_boot(std_struct: Module) -> Boot:
    return await Boot.create(
        root_module=std_struct
    )


@pytest_asyncio.fixture
async def run_std(std_struct: Module):
    await Boot.create(std_struct)


@pytest_asyncio.fixture
async def std_mongo_boot(std_struct: Module) -> Boot:
    return await Boot.create(
        root_module=std_struct
    )


@pytest.fixture
def set_prod_mode():
    os.environ["ORWYNN_MODE"] = "prod"


@pytest.fixture
def set_dev_mode():
    os.environ["ORWYNN_MODE"] = "dev"


@pytest.fixture
def set_test_mode():
    os.environ["ORWYNN_MODE"] = "test"


@pytest.fixture
def set_std_apprc_path_env() -> None:
    os.environ["ORWYNN_RC_PATH"] = os.path.join(
        os.getcwd(),
        "tests/std/orwynn.yml"
    )


@pytest.mark.asyncio
async def test_init_mode_default(std_struct: Module):
    """
    Default mode should be DEV.
    """
    os.environ["ORWYNN_MODE"] = ""
    boot: Boot = await Boot.create(
        root_module=std_struct,
        apprc={
            "dev": {
                "Mongo": {
                    "url": "mongodb://localhost:9006",
                    "database_name": "orwynn_test"
                }
            }
        }
    )
    assert boot.mode == AppMode.DEV


@pytest.mark.asyncio
async def test_init_mode_test(std_struct: Module):
    os.environ["ORWYNN_MODE"] = "test"
    boot: Boot = await Boot.create(
        root_module=std_struct,
        apprc={
            "test": {
                "Mongo": {
                    "url": "mongodb://localhost:9006",
                    "database_name": "orwynn_test"
                }
            }
        }
    )
    assert boot.mode == AppMode.TEST


@pytest.mark.asyncio
async def test_init_mode_dev(std_struct: Module):
    os.environ["ORWYNN_MODE"] = "dev"
    boot: Boot = await Boot.create(
        root_module=std_struct,
        apprc={
            "dev": {
                "Mongo": {
                    "url": "mongodb://localhost:9006",
                    "database_name": "orwynn_test"
                }
            }
        }
    )
    assert boot.mode == AppMode.DEV


@pytest.mark.asyncio
async def test_init_mode_prod(std_struct: Module):
    os.environ["ORWYNN_MODE"] = "prod"
    boot: Boot = await Boot.create(
        root_module=std_struct,
        apprc={
            "prod": {
                "Mongo": {
                    "url": "mongodb://localhost:9006",
                    "database_name": "orwynn_test"
                }
            }
        }
    )
    assert boot.mode == AppMode.PROD


@pytest.mark.asyncio
async def test_init_incorrect_mode(std_struct: Module):
    os.environ["ORWYNN_MODE"] = "helloworld"
    await validation.expect_async(
        Boot.create(root_module=std_struct),
        ValueError
    )


@pytest.mark.asyncio
async def test_init_enable_mongo(std_struct: Module, set_std_apprc_path_env):
    await Boot.create(
        root_module=std_struct
    )

    validation.validate(Di.ie().find("Mongo"), Mongo)


@pytest.mark.asyncio
async def test_nested_configs_prod(
    std_struct: Module,
    set_std_apprc_path_env,
    set_prod_mode
):
    await Boot.create(
        root_module=std_struct
    )
    app_rc: AppRc = BootProxy.ie().apprc
    text_config: TextConfig = Di.ie().find("TextConfig")

    assert app_rc["Text"]["words_amount"] == text_config.words_amount == 1


@pytest.mark.asyncio
async def test_nested_configs_dev(
    std_struct: Module,
    set_std_apprc_path_env,
    set_dev_mode
):
    await Boot.create(
        root_module=std_struct
    )
    app_rc: AppRc = BootProxy.ie().apprc
    text_config: TextConfig = Di.ie().find("TextConfig")

    assert app_rc["Text"]["words_amount"] == text_config.words_amount == 2


@pytest.mark.asyncio
async def test_nested_configs_test(
    std_struct: Module,
    set_std_apprc_path_env,
    set_test_mode
):
    await Boot.create(
        root_module=std_struct
    )
    app_rc: AppRc = BootProxy.ie().apprc
    text_config: TextConfig = Di.ie().find("TextConfig")

    assert app_rc["Text"]["words_amount"] == text_config.words_amount == 3


@pytest.fixture
def __gmodule() -> Module:
    return Module(
        "/gmodule",
        Providers=[_GService],
        exports=[_GService]
    )

@pytest.mark.asyncio
async def test_global_modules(
    __gmodule: Module
):
    class C1(HttpController):
        Route = "/"
        Endpoints = [Endpoint(method="get")]

        def __init__(self, gservice: _GService) -> None:
            super().__init__()
            self.__gservice: _GService = gservice

        def get(self) -> dict:
            return {"value": self.__gservice.calculate(1, 2, 3)}

    boot: Boot = await Boot.create(
        root_module=Module("/", Controllers=[C1]),
        global_modules=[__gmodule]
    )

    data: dict = boot.app.client.get_jsonify("/", 200)

    assert data["value"] == 6


@pytest.mark.asyncio
async def test_global_modules_reimported(
    __gmodule: Module
):
    """No module can import globally-defined modules."""
    class C1(HttpController):
        Route = "/"
        Endpoints = [Endpoint(method="get")]

        def __init__(self, gservice: _GService) -> None:
            super().__init__()
            self.__gservice: _GService = gservice

        def get(self) -> dict:
            return {"value": self.__gservice.calculate(1, 2, 3)}

    await validation.expect_async(
        Boot.create(
            # Root module reimports globally defined module
            root_module=Module("/", Controllers=[C1], imports=[__gmodule]),
            global_modules=[__gmodule]
        ),
        CircularDependencyError
    )
