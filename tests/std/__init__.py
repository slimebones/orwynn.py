"""Standard app structure made up for testing.
"""
from orwynn.app.app_service import AppService
from orwynn.base.module.module import Module
from orwynn.di.di_object.provider import Provider

from tests.std.text import TextConfig, TextService, text_module
from tests.std.number import NumberService, number_module
from tests.std.float import float_module, FloatService

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
    COLLECTED_PROVIDERS: list[type[Provider]] = [
        AppService,
        TextService,
        TextConfig,
        NumberService,
        FloatService
    ]
