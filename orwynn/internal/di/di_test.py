from pytest import fixture

from orwynn.boot._Boot import Boot
from orwynn.internal.di.collecting.provider_dependencies_map import (
    ProviderDependenciesMap,
)
from orwynn.internal.di.DiContainer import DiContainer
from orwynn.internal.di.init.init_providers import init_providers
from orwynn.base.module._Module import Module


@fixture
def std_di_container(
    std_struct: Module,
    std_provider_dependencies_map: ProviderDependenciesMap
) -> DiContainer:
    Boot(std_struct)
    return init_providers(std_provider_dependencies_map)
