from orwynn.base.module.module import Module
from orwynn.di.di import DI


def test_std(std_struct: Module):
    DI(std_struct)
