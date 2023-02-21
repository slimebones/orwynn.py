from orwynn.src.config.Config import Config
from orwynn.src.di.Provider import Provider
from orwynn.src.service.FrameworkService import FrameworkService
from orwynn.src.service.Service import Service

"""List of builtin classes in Provider category.

Providers with higher priority cannot inject ones with lower priority.

This list: Lower index => higher priority.
"""
BUILTIN_PROVIDERS: list[type[Provider]] = [
    Config,
    FrameworkService,
    Service
]
