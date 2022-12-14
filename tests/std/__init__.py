"""Standard app structure made up for testing.
"""
from orwynn.app.app_service import AppService
from orwynn.base.module.module import Module
from orwynn.boot.boot_config import BootConfig
from orwynn.di.acceptor import Acceptor
from orwynn.di.provider import Provider
from tests.std.float import FloatController, FloatService, float_module
from tests.std.number import NumberController, NumberService, number_module
from tests.std.text import TextConfig, TextController, TextService, text_module

root_module = Module(
    route="/",
    imports=[text_module, number_module]
)


class Assertion:
    COLLECTED_MODULES: list[Module] = [
        root_module,
        text_module,
        number_module,
        float_module
    ]
    # Order of these providers doesn't matter here since set() should be
    # performed on tests
    COLLECTED_PROVIDERS: list[type[Provider]] = [
        AppService,
        TextService,
        TextConfig,
        NumberService,
        FloatService,
        BootConfig
    ]
    COLLECTED_OTHER_ACCEPTORS: list[type[Acceptor]] = [
        TextController,
        NumberController,
        FloatController
    ]
