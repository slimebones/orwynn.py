from orwynn.src.boot.Boot import Boot
from orwynn.src.di.collecting.provider_dependencies_map import (
    ProviderDependenciesMap,
)
from orwynn.src.di.DiContainer import DiContainer
from orwynn.src.di.init.init_providers import init_providers
from orwynn.src.module.Module import Module
from tests.std.Assertion import Assertion


def test_std(
    std_struct: Module,
    std_provider_dependencies_map: ProviderDependenciesMap
):
    Boot(std_struct)
    container: DiContainer = init_providers(
        std_provider_dependencies_map
    )

    for P in Assertion.COLLECTED_PROVIDERS:
        isinstance(container.find(P.__name__), P)
