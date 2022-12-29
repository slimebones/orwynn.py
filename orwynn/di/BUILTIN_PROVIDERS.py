from orwynn.config.Config import Config
from orwynn.di.provider import Provider
from orwynn.service.framework_service import FrameworkService
from orwynn.service.Service import Service

"""List of builtin classes in Provider category.

Providers with lower priority cannot inject ones with higher priority.
"""
BUILTIN_PROVIDERS: list[type[Provider]] = [
    Config,
    FrameworkService,
    Service
]
