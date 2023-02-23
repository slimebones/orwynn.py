from pytest import fixture

from orwynn.boot.Boot import Boot
from orwynn.di.collecting.provider_dependencies_map import (
    ProviderDependenciesMap,
)
from orwynn.di.DiContainer import DiContainer
from orwynn.di.init.init_providers import init_providers
from orwynn.base.module.Module import Module


@fixture
def std_di_container(
    std_struct: Module,
    std_provider_dependencies_map: ProviderDependenciesMap
) -> DiContainer:
    Boot(std_struct)
    return init_providers(std_provider_dependencies_map)
