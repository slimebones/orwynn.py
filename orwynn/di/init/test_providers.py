from orwynn.di.collecting.providerdependenciesmap import (
    ProviderDependenciesMap,
)
from orwynn.di.container import DiContainer
from orwynn.di.init.providers import init_providers
from orwynn.base.module.module import Module
from orwynn.boot.boot import Boot
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
