from orwynn.base.module.root_module import RootModule
from orwynn.di.di import DI


def test_std(root_module: RootModule):
    di = DI(root_module)