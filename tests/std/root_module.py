"""Standard app structure made up for testing.
"""
from orwynn.src.module.Module import Module
from orwynn.src.mongo import module
from tests.std.number import number_module
from tests.std.text import text_module

root_module = Module(
    route="/",
    imports=[text_module, number_module, module.module]
)
