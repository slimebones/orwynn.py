"""Standard app structure made up for testing.
"""
import collections
from orwynn.app.app_service import AppService
from orwynn.base.module.module import Module
from orwynn.base.module.root_module import RootModule

from .number import number_module
from .text import text_module

root_module = RootModule(
    RootServices=[AppService],
    imports=[text_module, number_module]
)


class Assertion:
    COLLECTED_MODULES: list[Module] = [
        root_module,
        text_module,
        number_module
    ]
