from orwynn.di.collecting.no_dependencies_for_given_provider import \
    NoDependenciesForGivenProvider
from orwynn.di.collecting.provider_already_initialized_for_map_error import \
    ProviderAlreadyInitializedForMapError
from orwynn.di.collecting.provider_not_found_in_map_error import \
    ProviderNotFoundInMapError
from orwynn.di.di_object.provider import Provider


class ProvidersDependenciesMap:
    """Maps Providers and their requested dependencies.

    Since providers can request only other providers, it's a representation of
    Provider to Provider map.
    """

    # TODO:
    #   Rewrite to some analog in Collections module instead of this mess. Main
    #   objective is to restrict some operations on underlying dict.

    def __init__(
        self
    ) -> None:
        self._map: dict[type[Provider], list[type[Provider]]] = {}

    @property
    def Providers(self) -> list[type[Provider]]:
        return [P for P in self._map.keys()]

    @property
    def mapped_items(self):
        return self._map.items()

    def get_dependencies(self, P: type[Provider]) -> list[type[Provider]]:
        """Gets dependencies for given provider.

        Args:
            P:
                Provider to fetch dependencies from.

        Returns:
            List of dependencies of provider.

        Raises:
            ProviderNotFoundInMapError:
                Provider is not found.
            NoDependenciesForProviderError:
                No dependencies for given Provider is found.
        """
        res = self._map.get(P, None)
        if res:
            return res
        elif res == []:
            raise NoDependenciesForGivenProvider(P=P)
        else:
            raise ProviderNotFoundInMapError(P=P)

    def init_provider(
        self,
        P: type[Provider]
    ) -> None:
        """Initialize given Provider in the map.

        Args:
            P:
                Provider to be initialized.

        Raises:
            ProviderAlreadyInitializedForMapError:
                Provider already exists in the map.
        """
        if P in self._map:
            raise ProviderAlreadyInitializedForMapError(FailedProvider=P)
        self._map[P] = []

    def add_dependency(
        self, *, dependency: type[Provider], P: type[Provider]
    ) -> None:
        """Adds dependency for Provider.

        Creates a new Provider entry in the map if it's not exist.

        Args:
            dependency:
                Dependency to add.
            P:
                Provider to add to.
        """
        if P in self._map:
            self._map[P].append(dependency)
        else:
            self._map[P] = [dependency]
