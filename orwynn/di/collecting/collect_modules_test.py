from pytest import fixture

from orwynn.base.module.module import Module
from orwynn.di.circular_dependency_error import CircularDependencyError
from orwynn.di.collecting.collect_modules import collect_modules
from tests.std import Assertion


@fixture
def std_modules(std_struct: Module) -> list[Module]:
    return collect_modules(std_struct)


def test_std(std_struct: Module):
    collected_modules = collect_modules(std_struct)

    assert collected_modules == Assertion.COLLECTED_MODULES


def test_imports_self(self_importing_module_struct: Module):
    try:
        collect_modules(self_importing_module_struct)
    except CircularDependencyError:
        pass
    else:
        raise AssertionError("CircularDependencyError expected")


def test_circular(circular_module_struct: Module):
    try:
        collect_modules(circular_module_struct)
    except CircularDependencyError:
        pass
    else:
        raise AssertionError("CircularDependencyError expected")


def test_long_circular(long_circular_module_struct: Module):
    try:
        collect_modules(long_circular_module_struct)
    except CircularDependencyError:
        pass
    else:
        raise AssertionError("CircularDependencyError expected")
