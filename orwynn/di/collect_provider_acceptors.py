import inspect
from orwynn.base.config.config import Config

from orwynn.base.model.model import Model
from orwynn.base.module.module import Module
from orwynn.base.module.root_module import RootModule
from orwynn.di.circular_dependency_error import CircularDependencyError
from orwynn.di.is_provider import is_provider
from orwynn.di.not_provider_error import NotProviderError
from orwynn.di.provider_already_initialized_for_map_error import ProviderAlreadyInitializedForMapError
from orwynn.di.provider_not_available_error import ProviderNotAvailableError
from orwynn.util.format_chain import format_chain
from orwynn.util.types.acceptor import Acceptor
from orwynn.util.types.provider import Provider

_ProviderParameters = list["_ProviderParameter"]


class ProvidersAcceptorsMap:
    """Maps Providers and their Acceptors.
    """
    def __init__(self) -> None:
        self._map: dict[type[Provider], list[type[Acceptor]]] = {}

    @property
    def Providers(self) -> list[type[Provider]]:
        return [P for P in self._map.keys()]

    def init_provider(
        self,
        P: type[Provider],
        is_strict: bool = True
    ) -> None:
        """Initialize given Provider in the map.
        
        Args:
            P:
                Provider to be initialized.

        Raises:
            ProviderAlreadyInitializedForMapError:
                Provider already exists in the map. 
        """
        if P in self._map and is_strict:
            raise ProviderAlreadyInitializedForMapError(FailedProvider=P)
        self._map[P] = []

    def add_acceptor(self, A: type[Acceptor], P: type[Provider]) -> None:
        """Adds given Acceptor for Provider.

        Creates a new Provider entry in the map if it's not exist.
        
        Args:
            A:
                Acceptor to add.
            P:
                Provider to add to.
        """
        if P in self._map:
            self._map[P].append(A)
        else:
            self._map[P] = [A]


class _ProviderParameter(Model):
    name: str
    RequiredProvider: type[Provider]


def collect_provider_acceptors(
    modules: list[Module]
) -> ProvidersAcceptorsMap:
    """Collects providers and their acceptors from given modules.
    
    Args:
        modules:
            List of modules to collect providers from.

    Returns:
        Special structure maps providers to their acceptors. 
    """
    metamap: ProvidersAcceptorsMap = ProvidersAcceptorsMap()

    # Traverse all parameters of all providers in all modules to add them in
    # united structure
    for module in modules:
        for P in module.Providers:
            # Chain is cleared for every new provider iterated
            _traverse(P, metamap, [], module)

    return metamap


def _traverse(
    P: type[Provider],
    metamap: ProvidersAcceptorsMap,
    chain: list[type[Provider]],
    target_module: Module
):
    # Recursively traverses over Provider parameters, memorizing chain to
    # find circular dependencies and saving results to metamap.  Target module
    # required since we want to check availability between providers.

    if P in chain:
        raise CircularDependencyError(
            "{} occured twice in dependency chain {}"
            .format(
                P,
                # Failed provider is added second time to the chain for
                # error descriptiveness
                format_chain(chain + [P])
            )
        )
    chain.append(P)
    metamap.init_provider(P, is_strict=False)

    for parameter in _get_parameters_for_provider(P):
        print(P, " | ", parameter)
        if not is_provider(parameter.RequiredProvider):
            if issubclass(P, Config):
                continue
            raise NotProviderError(
                FailedClass=parameter.RequiredProvider
            ) 

        target_module = _check_availability(
            P,
            parameter.RequiredProvider,
            target_module
        )
        metamap.add_acceptor(P, parameter.RequiredProvider)
        _traverse(parameter.RequiredProvider, metamap, chain, target_module)

    # Pop blocking element.  For this concept see collect_modules._traverse
    # function
    chain.pop()


def _check_availability(
    P1: type[Provider],
    P2: type[Provider],
    P1_module: Module
) -> Module:
    # Check if P2 is available to P1, module is required to start searching
    # from.  Returns the module where P2 is located.

    for P in P1_module.Providers:
        if P is P2:
            # Available within the same module
            return P1_module
    
    # Not available in the same module, check imported ones
    for m in P1_module.imports:
        for P in m.exports:
            if P is P2:
                # Available in the exports of the imported module
                return m

    raise ProviderNotAvailableError(Provider1=P1, Provider2=P2)


def _get_parameters_for_provider(
    Provider: type[Provider]
) -> _ProviderParameters:
    # Inspects the provider and returns requested by it parameters.

    return [
        _ProviderParameter(
            name=inspect_parameter.name,
            RequiredProvider=inspect_parameter.annotation
        )  
            for inspect_parameter in
            inspect.signature(Provider).parameters.values()
    ]