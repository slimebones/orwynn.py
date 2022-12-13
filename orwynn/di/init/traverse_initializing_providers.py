import inspect
from orwynn.base.config.config import Config
from orwynn.di.circular_dependency_error import CircularDependencyError
from orwynn.di.collecting.no_dependencies_for_given_provider_error import \
    NoDependenciesForGivenProviderError
from orwynn.di.collecting.provider_dependencies_map import \
    ProvidersDependenciesMap
from orwynn.di.di_object.di_container import DIContainer
from orwynn.di.di_object.is_provider import is_provider
from orwynn.di.di_object.missing_di_object_error import MissingDIObjectError
from orwynn.di.di_object.provider import Provider
from orwynn.util.fmt import format_chain


def traverse_initializing_providers(
    providers_dependencies_map: ProvidersDependenciesMap
) -> DIContainer:
    """Traverses through given providers and dependencies initializing them.

    Args:
        providers_dependencies_map:
            Map of providers and their dependencies.

    Returns:
        DI container populated with initialized providers by their names.
    """

    # Note for this module that most validation logic has been already
    # performed at previous stages, so no need to do checks here.

    container: DIContainer = DIContainer()

    for P in providers_dependencies_map.Providers:
        try:
            container.find(P.__name__)
        except MissingDIObjectError:
            _traverse(
                StarterProvider=P,
                mp=providers_dependencies_map,
                container=container,
                chain=[]
            )

    return container


def _traverse(
    *,
    StarterProvider: type[Provider],
    mp: ProvidersDependenciesMap,
    container: DIContainer,
    chain: list[type[Provider]]
) -> Provider:
    print(StarterProvider, container.items)
    already_initialized_dependencies: list[Provider] = []

    if StarterProvider in chain:
        raise CircularDependencyError(
            "provider {} occured twice in dependency chain {}"
            .format(
                StarterProvider,
                # Failed provider is added second time to the chain for
                # error descriptiveness
                format_chain(chain + [StarterProvider])
            )
        )

    try:
        Dependencies: list[type[Provider]] = mp.get_dependencies(
            StarterProvider
        )
    except NoDependenciesForGivenProviderError:
        # Final point in chain, since no dependencies we can initialize
        # without any attributes
        pass
    else:
        chain.append(StarterProvider)

        for D in Dependencies:
            try:
                already_initialized_dependencies.append(
                    container.find(D.__name__)
                )
            except MissingDIObjectError:
                already_initialized_dependencies.append(
                    _traverse(
                        StarterProvider=D,
                        mp=mp,
                        container=container,
                        chain=chain
                    )
                )

        # On object initialization it should be removed from chain, but not for
        # Config since it hasn't been appended
        chain.pop()

    # All dependencies for this provider have been initialized - now initialize
    # this provider. Checks on previous phases should have validated, that
    # every provider waits only positional arguments.
    result_provider: Provider
    if issubclass(StarterProvider, Config):
        # For configs we need to prepare names kwargs, so we perform
        # signaturing and container searching here once again. It's not good
        # since we've done it before, so consider refactoring.
        provider_kwargs: dict[str, Provider] = {}

        for param in inspect.signature(StarterProvider).parameters.values():
            if is_provider(param.annotation):
                provider_kwargs[param.name] = container.find(
                    param.annotation.__name__
                )

        result_provider = StarterProvider.fw_create(provider_kwargs)
    else:
        result_provider = StarterProvider(
            *already_initialized_dependencies
        )  # type: ignore

    container.add(result_provider)
    return result_provider
