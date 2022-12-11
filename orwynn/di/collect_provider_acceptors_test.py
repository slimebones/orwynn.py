from pytest import fixture
from orwynn.base.module.module import Module
from orwynn.base.module.root_module import RootModule
from orwynn.di.circular_dependency_error import CircularDependencyError
from orwynn.di.collect_modules import collect_modules
from orwynn.di.collect_provider_acceptors import (ProvidersAcceptorsMap,
                                                  collect_provider_acceptors)
from orwynn.di.objects.provider import Provider
from tests.std import Assertion


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
def long_twice_occurence_structure() -> RootModule:
    m1 = Module(route="/m1")
    m2 = Module(route="/m2", imports=[m1])
    m3 = Module(route="/m3", imports=[m2])
    m4 = Module(route="/m4", imports=[m3])

    m1.imports.append(m4)

    rm = RootModule(
        imports=[m1]
    )

    return rm


def test_std(std_structure: RootModule):
    metamap: ProvidersAcceptorsMap = collect_provider_acceptors(
        collect_modules(std_structure)
    )

    assert metamap.Providers == Assertion.COLLECTED_PROVIDERS


def test_twice_occurence(twice_occurence_structure: RootModule):
    try:
        collect_provider_acceptors(
            collect_modules(twice_occurence_structure)
        )
    except CircularDependencyError:
        pass
    else:
        raise AssertionError("CircularDependencyError expected")


def test_long_twice_occurence(long_twice_occurence_structure: RootModule):
    try:
        collect_provider_acceptors(
            collect_modules(long_twice_occurence_structure)
        )
    except CircularDependencyError:
        pass
    else:
        raise AssertionError("CircularDependencyError expected")