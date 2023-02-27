"""Standard app structure made up for testing.
"""
from orwynn.base.module._Module import Module
from orwynn import mongo
from tests.std.number import number_module
from tests.std.text import text_module

root_module = Module(
    route="/",
    imports=[text_module, number_module, mongo.module]
)
