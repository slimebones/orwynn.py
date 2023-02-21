from pytest import fixture

from orwynn.src.boot.Boot import Boot
from orwynn.src.di.collecting.provider_dependencies_map import (
    ProviderDependenciesMap,
)
from orwynn.src.di.DiContainer import DiContainer
from orwynn.src.di.init.init_providers import init_providers
from orwynn.src.module.Module import Module


@fixture
def std_di_container(
    std_struct: Module,
    std_provider_dependencies_map: ProviderDependenciesMap
) -> DiContainer:
    Boot(std_struct)
    return init_providers(std_provider_dependencies_map)
