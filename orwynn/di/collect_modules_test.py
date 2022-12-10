from orwynn.base.module.root_module import RootModule
from orwynn.di.collect_modules import collect_modules
from tests.std import Assertion


def test_std(root_module: RootModule):
    collected_modules = collect_modules(root_module)

    assert collected_modules == Assertion.COLLECTED_MODULES