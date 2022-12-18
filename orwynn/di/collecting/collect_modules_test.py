from pytest import fixture

from orwynn.base.module import Module
from orwynn.di.circular_dependency_error import CircularDependencyError
from orwynn.di.collecting.collect_modules import collect_modules
from orwynn.util.expect import expect
from tests.std.Assertion import Assertion


@fixture
def std_modules(std_struct: Module) -> list[Module]:
    return collect_modules(std_struct)


def test_std(std_struct: Module):
    collected_modules = collect_modules(std_struct)

    assert collected_modules == Assertion.COLLECTED_MODULES


def test_imports_self(self_importing_module_struct: Module):
    expect(
        collect_modules, CircularDependencyError, self_importing_module_struct
    )


def test_circular(circular_module_struct: Module):
    expect(
        collect_modules, CircularDependencyError, circular_module_struct
    )


def test_long_circular(long_circular_module_struct: Module):
    expect(
        collect_modules, CircularDependencyError, long_circular_module_struct
    )
