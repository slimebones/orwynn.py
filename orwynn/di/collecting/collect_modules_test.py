from pytest import fixture

from orwynn.base.module.module import Module
from orwynn.di.circular_dependency_error import CircularDependencyError
from orwynn.di.collecting.collect_modules import collect_modules
from tests.std import Assertion


@fixture
def std_modules(std_struct: Module) -> list[Module]:
    return collect_modules(std_struct)


@fixture
def self_importing_struct() -> Module:
    m1 = Module(route="/m1")
    m1.imports.append(m1)
    return Module(
        route="/",
        imports=[m1]
    )


@fixture
def twice_occurence_struct() -> Module:
    m1 = Module(route="/m1")
    m2 = Module(route="/m2", imports=[m1])

    m1.imports.append(m2)

    rm = Module(
        route="/",
        imports=[m1]
    )

    return rm


def test_std(std_struct: Module):
    collected_modules = collect_modules(std_struct)

    assert collected_modules == Assertion.COLLECTED_MODULES


def test_imports_self(self_importing_struct: Module):
    try:
        collect_modules(self_importing_struct)
    except CircularDependencyError:
        pass
    else:
        raise AssertionError("CircularDependencyError expected")


def test_occured_twice(twice_occurence_struct: Module):
    try:
        collect_modules(twice_occurence_struct)
    except CircularDependencyError:
        pass
    else:
        raise AssertionError("CircularDependencyError expected")
