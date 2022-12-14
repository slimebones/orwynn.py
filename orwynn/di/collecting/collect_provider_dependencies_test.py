import inspect

from pytest import fixture

from orwynn.base.config.config import Config
from orwynn.base.module.module import Module
from orwynn.di.circular_dependency_error import CircularDependencyError
from orwynn.di.collecting.collect_modules import collect_modules
from orwynn.di.collecting.collect_provider_dependencies import (
    ProviderDependenciesMap, collect_provider_dependencies)
from orwynn.di.is_provider import is_provider
from orwynn.di.provider import Provider
from tests.std import STD_FRAMEWORK_SERVICES, Assertion


@fixture
def std_provider_dependencies_map(
    std_modules: list[Module]
) -> ProviderDependenciesMap:
    return collect_provider_dependencies(std_modules, STD_FRAMEWORK_SERVICES)


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


@fixture
def long_twice_occurence_struct() -> Module:
    m1 = Module(route="/m1")
    m2 = Module(route="/m2", imports=[m1])
    m3 = Module(route="/m3", imports=[m2])
    m4 = Module(route="/m4", imports=[m3])

    m1.imports.append(m4)

    rm = Module(
        route="/",
        imports=[m1]
    )

    return rm


def test_std(std_struct: Module):
    metamap: ProviderDependenciesMap = collect_provider_dependencies(
        collect_modules(std_struct),
        STD_FRAMEWORK_SERVICES
    )

    # Order doesn't matter
    assert set(metamap.Providers) == set(Assertion.COLLECTED_PROVIDERS)

    for P, dependencies in metamap.mapped_items:
        assertion_dependencies: list[type[Provider]] = []
        for inspect_parameter in inspect.signature(P).parameters.values():
            # Skip config's parseable parameters
            if (
                issubclass(P, Config)
                and not is_provider(inspect_parameter.annotation)
            ):
                continue
            assertion_dependencies.append(inspect_parameter.annotation)
        assert dependencies == assertion_dependencies


def test_twice_occurence(twice_occurence_struct: Module):
    try:
        collect_provider_dependencies(
            collect_modules(twice_occurence_struct),
            STD_FRAMEWORK_SERVICES
        )
    except CircularDependencyError:
        pass
    else:
        raise AssertionError("CircularDependencyError expected")


def test_long_twice_occurence(long_twice_occurence_struct: Module):
    try:
        collect_provider_dependencies(
            collect_modules(long_twice_occurence_struct),
            STD_FRAMEWORK_SERVICES
        )
    except CircularDependencyError:
        pass
    else:
        raise AssertionError("CircularDependencyError expected")
