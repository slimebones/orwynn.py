import inspect

from orwynn.base.config.config import Config
from orwynn.base.model.model import Model
from orwynn.base.module.module import Module
from orwynn.base.service.framework_service import FrameworkService
from orwynn.di.circular_dependency_error import CircularDependencyError
from orwynn.di.collecting.not_provider_error import NotProviderError
from orwynn.di.collecting.provider_already_initialized_for_map_error import \
    ProviderAlreadyInitializedForMapError
from orwynn.di.collecting.provider_dependencies_map import \
    ProviderDependenciesMap
from orwynn.di.collecting.provider_keyword_attribute_error import \
    ProviderKeywordAttributeError
from orwynn.di.collecting.provider_not_available_error import \
    ProviderNotAvailableError
from orwynn.di.di_error import DIError
from orwynn.di.is_provider import is_provider
from orwynn.di.provider import Provider
from orwynn.util.fmt import format_chain

_ProviderParameters = list["_ProviderParameter"]


class _ProviderParameter(Model):
    name: str
    DependencyProvider: type[Provider]


def collect_provider_dependencies(
    modules: list[Module],
    FrameworkServices: list[type[FrameworkService]]
) -> ProviderDependenciesMap:
    """Collects providers and their dependencies from given modules.

    Args:
        modules:
            List of modules to collect providers from.
        FrameworkServices:
            Framework-level services to collect first.

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
            "provider {} occured twice in dependency chain {}"
            .format(
                P,
                # Failed provider is added second time to the chain for
                # error descriptiveness
                format_chain(chain + [P])
            )
        )
    chain.append(P)

    try:
        metamap.init_provider(P)
    except ProviderAlreadyInitializedForMapError:
        pass
    else:
        for parameter in _get_parameters_for_provider(P):
            if not is_provider(parameter.DependencyProvider):
                # Config's fields are skipped since they request various other
                # than provider objects and will be initialized in a bit
                # different way
                if issubclass(P, Config):
                    continue
                raise NotProviderError(
                    FailedClass=parameter.DependencyProvider
                )

            nested_module: Module | None = _check_availability(
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

    # Pop blocking element.  For this concept see collect_modules._traverse
    # function
    chain.pop()


def _check_availability(
    P1: type[Provider],
    P2: type[Provider],
    P1_module: Module | None
) -> Module | None:
    # Check if P2 is available to P1, module is required to start searching
    # from. Returns the module where P2 is located or None if P2 is a
    # FrameworkService.

    # If P1_module is None, this means that we entered a Framework scope and
    # will be serarching there.

    # Note, that this function is not checking provider priorities. So it's
    # possible to see positive output here for lower-priority provider
    # requesting higher-priority one, which in general logic shouldn't
    # be possible.

    # Resolve cases with frameworks services right away:
    #   - P1 cannot be a FrameworkService, since nothing is available for it in
    #       user's scope
    #   - If P2 is a FrameworkService, we can be assured that it is available
    #       for any other requested Provider, except for cases, if requested
    #       Provider is a Config.
    #
    # In all other cases raise a ProviderNotAvailableError.
    is_error: bool
    res: Module | None = None

    if issubclass(P1, FrameworkService):
        is_error = True
    elif issubclass(P2, FrameworkService) and not issubclass(P1, Config):
        is_error = False
    elif P1_module is not None:
        found_module = _search_matching_provider(
            target_module=P1_module,
            TargetProvider=P2
        )
        if found_module is None:
            is_error = True
        else:
            is_error = False
            res = found_module
    else:
        raise DIError(
            f"not logical to check availability between {P1} -> {P2} in"
            + " framework's scope"
        )

    if is_error:
        raise ProviderNotAvailableError(Provider1=P1, Provider2=P2)
    else:
        return res


def _search_matching_provider(
    target_module: Module,
    TargetProvider: type[Provider]
) -> Module | None:
    # Searches for the provider in module. Returns tuple signifies module,
    # where provider was found, or None, it it wasn't.

    res: Module | None = None
    is_found: bool = False

    for P in target_module.Providers:
        if P is TargetProvider:
            # Available within the same module
            is_found = True
            res = target_module

    if not is_found:
        # Not available in the same module, check imported ones
        for m in target_module.imports:
            for P in m.exports:
                if P is TargetProvider:
                    # Available in the exports of the imported module
                    is_found = True
                    res = m

    return res


def _get_parameters_for_provider(
    Provider: type[Provider]
) -> _ProviderParameters:
    # Inspects the provider and returns requested by it parameters.

    parameters: _ProviderParameters = []

    for inspect_parameter in inspect.signature(Provider).parameters.values():
        if (
            inspect_parameter.kind is inspect._ParameterKind.KEYWORD_ONLY
            and not issubclass(Provider, Config)
        ):
            raise ProviderKeywordAttributeError(
                f"provider {Provider} cannot have keyword only attributes"
            )

        # Note that on this stage all config parameters (even not providers) is
        # added, and later on additional checks is performed. Actually this
        # doesn't have much sense to not filter such non-provider parameters
        # here, and in future it might be refactored. But from other side it
        # might be useful later on to perform additional logic in DI's scope
        # on Config's non-provider fields, such as checking if it is not
        # waiting for other providers but i'm not sure that it's the case.

        parameters.append(
            _ProviderParameter(
                name=inspect_parameter.name,
                DependencyProvider=inspect_parameter.annotation
            )
        )

    return parameters
