from orwynn.base.config import Config
from orwynn.base.mapping import Mapping
from orwynn.base.service.framework_service import FrameworkService
from orwynn.base.service import Service
from orwynn.di.provider import Provider


"""List of builtin classes in Provider category.

Providers with lower priority cannot inject ones with higher priority.
"""
BUILTIN_PROVIDERS: list[type[Provider]] = [
    Config,
    FrameworkService,
    Service
]
