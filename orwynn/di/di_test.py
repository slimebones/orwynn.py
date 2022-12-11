from orwynn.base.module.root_module import RootModule
from orwynn.di.di import DI


def test_std(std_structure: RootModule):
    DI(std_structure)
