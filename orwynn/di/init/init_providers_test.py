from orwynn.boot.Boot import Boot
from orwynn.di.collecting.provider_dependencies_map import (
    ProviderDependenciesMap,
)
from orwynn.di.DIContainer import DIContainer
from orwynn.di.init.init_providers import init_providers
from tests.std.Assertion import Assertion

from orwynn.module.Module import Module


def test_std(
    std_struct: Module,
    std_provider_dependencies_map: ProviderDependenciesMap
):
    Boot(std_struct)
    container: DIContainer = init_providers(
        std_provider_dependencies_map
    )

    for P in Assertion.COLLECTED_PROVIDERS:
        isinstance(container.find(P.__name__), P)
