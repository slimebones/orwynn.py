from orwynn.di.collecting.provider_dependencies_map import \
    ProviderDependenciesMap
from orwynn.di.di_container import DIContainer
from orwynn.di.init.init_providers import init_providers
from tests.std.Assertion import Assertion


def test_std(
    std_provider_dependencies_map: ProviderDependenciesMap
):
    container: DIContainer = init_providers(
        std_provider_dependencies_map
    )

    for P in Assertion.COLLECTED_PROVIDERS:
        isinstance(container.find(P.__name__), P)
