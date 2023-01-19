from pytest import fixture

from orwynn.boot.Boot import Boot
from orwynn.di.collecting.provider_dependencies_map import (
    ProviderDependenciesMap,
)
from orwynn.di.DIContainer import DIContainer
from orwynn.di.init.init_providers import init_providers
from orwynn.module.Module import Module


@fixture
def std_di_container(
    std_struct: Module,
    std_provider_dependencies_map: ProviderDependenciesMap
) -> DIContainer:
    Boot(std_struct)
    return init_providers(std_provider_dependencies_map)
