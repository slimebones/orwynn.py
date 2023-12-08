"""Standard app structure made up for testing.
"""
from orwynn import mongo
from orwynn.module.module import Module
from tests.std.number import number_module
from tests.std.text import text_module

root_module = Module(
    route="/",
    imports=[text_module, number_module, mongo.module]
)
