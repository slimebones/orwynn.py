from orwynn.base.config import Config
from orwynn.base.module import Module
from orwynn.base.module.errors import CircularDependencyError
from orwynn.di.availability import check_availability
from orwynn.di.collecting.errors import (
    ProviderAlreadyInitializedForMapError,
)
from orwynn.di.collecting.helpers import (
    get_parameters_for_provider,
)
from orwynn.di.collecting.providerdependencies.map import (
    ProviderDependenciesMap,
)
from orwynn.di.errors import NotProviderError
from orwynn.di.isprovider import is_provider
from orwynn.di.provider import Provider
from orwynn.utils.fmt import format_chain


def collect_provider_dependencies(
    modules: list[Module]
) -> ProviderDependenciesMap:
    """Collects providers and their dependencies from given modules.

    Args:
        modules:
            List of modules to collect providers from.

    Returns:
        Special structure maps providers and their dependencies.
    """
    metamap: ProviderDependenciesMap = ProviderDependenciesMap()

    # Traverse all parameters of all providers in all modules to add them in
    # united structure
    for module in modules:
        for P in module.Providers:
            # Chain is cleared for every new provider iterated
            _traverse(P, metamap, [], module)

    return metamap


def _traverse(
    P: type[Provider],
    metamap: ProviderDependenciesMap,
    chain: list[type[Provider]],
    target_module: Module | None
):
    # Recursively traverses over Provider parameters, memorizing chain to
    # find circular dependencies and saving results to metamap.  Target module
    # required since we want to check availability between providers.

    if P in chain:
        raise CircularDependencyError(
            # Failed provider is added second time to the chain for
            # error descriptiveness
            f"provider {P} occured twice in dependency chain"
            f" {format_chain(chain + [P])}"
        )
    chain.append(P)

    try:
        metamap.init_provider(P)
    except ProviderAlreadyInitializedForMapError:
        pass
    else:
        for parameter in get_parameters_for_provider(P):
            if not is_provider(parameter.DependencyProvider):
                # Config's fields are skipped since they request various other
                # than provider objects and will be initialized in a bit
                # different way
                if issubclass(P, Config):
                    continue
                raise NotProviderError(
                    FailedClass=parameter.DependencyProvider
                )

            nested_module: Module | None = check_availability(
                P,
                parameter.DependencyProvider,
                target_module
            )
            metamap.add_dependency(
                dependency=parameter.DependencyProvider,
                P=P
            )
            # And continue traversing, but deeper for fetched dependency
            _traverse(
                parameter.DependencyProvider,
                metamap,
                chain,
                nested_module
            )

    # Pop blocking element. For this concept see collect_modules._traverse
    # function
    chain.pop()
