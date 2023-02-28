from orwynn._di.collecting.provider_dependencies_map import (
    ProviderDependenciesMap,
)
from orwynn._di.DiContainer import DiContainer
from orwynn._di.init.init_providers import init_providers
from orwynn.base.module._Module import Module
from orwynn.boot._Boot import Boot
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
