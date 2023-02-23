from orwynn.config.Config import Config
from orwynn.di.Provider import Provider
from orwynn.base.service.FrameworkService import FrameworkService
from orwynn.base.service.Service import Service

"""List of builtin classes in Provider category.

Providers with higher priority cannot inject ones with lower priority.

This list: Lower index => higher priority.
"""
BUILTIN_PROVIDERS: list[type[Provider]] = [
    Config,
    FrameworkService,
    Service
]
