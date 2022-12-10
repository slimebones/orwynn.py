from orwynn.base.module.module import Module
from orwynn.util.types.provider import Provider


def collect_providers(modules: list[Module]) -> list[Provider]:
    """Collects providers and their dependencies from given modules.
    
    Args:
        modules:
            List of modules to collect providers from.

    Returns:
        Providers collected.
    """
    pass