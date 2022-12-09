from orwynn.base.config.config import Config
from orwynn.base.mapping.mapping import Mapping
from orwynn.base.service.root_service import RootService
from orwynn.base.service.service import Service
from orwynn.util.types.provider import Provider


"""List of builtin classes in Provider category.

Providers with lower priority cannot inject ones with higher priority.
"""
BUILTIN_PROVIDERS: list[Provider] = [
    Config,
    RootService,
    Service,
    Mapping
]