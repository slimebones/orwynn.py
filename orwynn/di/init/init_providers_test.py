from pytest import fixture

from orwynn.base.module.module import Module
from orwynn.di.collecting.provider_dependencies_map import \
    ProviderDependenciesMap
from orwynn.di.di_container import DIContainer
from orwynn.di.init.init_providers import init_providers
from tests.std import Assertion


@fixture
def std_di_container(
    std_provider_dependencies_map: ProviderDependenciesMap
) -> DIContainer:
    return init_providers(std_provider_dependencies_map)


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


def test_std(std_provider_dependencies_map: ProviderDependenciesMap):
    container: DIContainer = init_providers(
        std_provider_dependencies_map
    )

    for P in Assertion.COLLECTED_PROVIDERS:
        isinstance(container.find(P.__name__), P)
