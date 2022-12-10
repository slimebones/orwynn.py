from pytest import fixture

from orwynn.base.module.module import Module
from orwynn.base.module.root_module import RootModule
from orwynn.di.circular_dependency_error import CircularDependencyError
from orwynn.di.collect_modules import collect_modules
from tests.std import Assertion


@fixture
def self_importing_structure() -> RootModule:
    m1 = Module(route="/m1")
    m1.imports.append(m1)
    return RootModule(
        imports=[m1]
    )


@fixture
def twice_occurence_structure() -> RootModule:
    m1 = Module(route="/m1")
    m2 = Module(route="/m2", imports=[m1])

    m1.imports.append(m2)

    rm = RootModule(
        imports=[m1]
    )

    return rm


@fixture
def imports_root_module_structure() -> RootModule:
    m1 = Module(route="/m1")
    rm = RootModule(
        imports=[m1]
    )
    m1.imports.append(rm)
    return rm


def test_std(std_structure: RootModule):
    collected_modules = collect_modules(std_structure)

    assert collected_modules == Assertion.COLLECTED_MODULES


def test_imports_self(self_importing_structure: RootModule):
    try:
        collect_modules(self_importing_structure)
    except CircularDependencyError:
        pass
    else:
        raise AssertionError("CircularDependencyError expected")


def test_occured_twice(twice_occurence_structure: RootModule):
    try:
        collect_modules(twice_occurence_structure)
    except CircularDependencyError:
        pass
    else:
        raise AssertionError("CircularDependencyError expected")


def test_imports_root_module(imports_root_module_structure: RootModule):
    try:
        collect_modules(imports_root_module_structure)
    except CircularDependencyError:
        pass
    else:
        raise AssertionError("CircularDependencyError expected")
