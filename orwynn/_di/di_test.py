from pytest import fixture

from orwynn._di.collecting.provider_dependencies_map import (
    ProviderDependenciesMap,
)
from orwynn._di.DiContainer import DiContainer
from orwynn._di.init.init_providers import init_providers
from orwynn.base.module._Module import Module
from orwynn.boot._Boot import Boot


@fixture
def std_di_container(
    std_struct: Module,
    std_provider_dependencies_map: ProviderDependenciesMap
) -> DiContainer:
    Boot(std_struct)
    return init_providers(std_provider_dependencies_map)
