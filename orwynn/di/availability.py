from orwynn.base.config import Config
from orwynn.base.module.module import Module
from orwynn.base.service.framework import FrameworkService
from orwynn.di.errors import NotProviderError, ProviderAvailabilityError
from orwynn.di.isprovider import is_provider
from orwynn.di.object import DiObject
from orwynn.di.provider import Provider


def check_availability(
    Requestor: type[DiObject],
    Target: type[Provider],
    requestor_module: Module | None
) -> Module | None:
    """
    Checks if the Target is available to Requestor.

    Note, that this function is not checking provider priorities. So it's
    possible to see positive output here for lower-priority provider
    requesting higher-priority one, which in general logic shouldn't
    be possible.

    Resolves cases with frameworks services right away:
    - If P2 is a FrameworkService, we can be assured that it is available
        for any other requested Provider, except for cases where the requested
        Provider is a Config, because the Config is the only class that has
        a higher priority than the FrameworkService.

    Args:
        Requestor:
            Which object is searching.
        Target:
            Provider search is made for.
        requestor_module:
            Module of the Requestor to start searching from.
            Can be set to None to search within the Framework's scope.

    Returns:
        module:
            The module where Target is located
        None:
            If the Target is a FrameworkService, 100% available
        None:
            If the Requestor is a FrameworkService and the Target is any
            Config because we 100% sure that Config will be available.

    Raises:
        ProviderAvailabilityError:
            The Target provider is not available for the Requestor.
    """
    is_error: bool
    res: Module | None = None

    # The Target should be provider
    if not is_provider(Target):
        raise NotProviderError(
            f"object {Target} is not a provider"
        )
    elif (
        issubclass(Requestor, FrameworkService) and issubclass(Target, Config)
        or (
            issubclass(Target, FrameworkService)
            and not issubclass(Requestor, Config)
        )
    ):
        is_error = False
    elif requestor_module is not None:
        found_module = __search_matching_provider(
            target_module=requestor_module,
            TargetProvider=Target
        )
        if found_module is None:
            is_error = True
        else:
            is_error = False
            res = found_module
    else:
        raise ProviderAvailabilityError(
            f"not logical to check an availability between {Requestor} ->"
            f" {Target} in the framework's scope"
        )

    if is_error:
        raise ProviderAvailabilityError(Provider1=Requestor, DiObject=Target)
    else:
        return res


def __search_matching_provider(
    target_module: Module,
    TargetProvider: type[Provider]
) -> Module | None:
    """
    Searches for the provider in module.

    Returns:
        The module where the provider was found, or None, it it wasn't.
    """

    res: Module | None = None
    is_found: bool = False

    for P in target_module.Providers:
        if P is TargetProvider:
            # Available within the same module
            is_found = True
            res = target_module

    if not is_found:
        # Not available in the same module, check the exports of the imported
        # ones
        for m in target_module._imports:
            for P in m._exports:
                if P is TargetProvider:
                    # Available in the exports of the imported module
                    is_found = True
                    res = m

    return res
