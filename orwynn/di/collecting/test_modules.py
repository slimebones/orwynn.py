from pytest import fixture

from orwynn.base.module.errors import CircularDependencyError
from orwynn.base.module.module import Module
from orwynn.di.collecting.modulecollector import ModuleCollector
from orwynn.utils.validation import expect
from tests.std.assertion import Assertion


@fixture
def std_modules(std_struct: Module) -> list[Module]:
    return ModuleCollector(std_struct).collected_modules


def test_std(std_struct: Module):
    collected_modules = ModuleCollector(std_struct).collected_modules

    assert collected_modules == Assertion.CollectedModules


def test_imports_self(self_importing_module_struct: Module):
    expect(
        ModuleCollector,
        CircularDependencyError,
        self_importing_module_struct
    )


def test_circular(circular_module_struct: Module):
    expect(
        ModuleCollector,
        CircularDependencyError,
        circular_module_struct
    )


def test_long_circular(long_circular_module_struct: Module):
    expect(
        ModuleCollector,
        CircularDependencyError,
        long_circular_module_struct
    )
