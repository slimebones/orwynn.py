from orwynn.config.Config import Config
from orwynn.internal.di.Provider import Provider
from orwynn.base.service._FrameworkService import FrameworkService
from orwynn.base.service._Service import Service

"""List of builtin classes in Provider category.

Providers with higher priority cannot inject ones with lower priority.

This list: Lower index => higher priority.
"""
BUILTIN_PROVIDERS: list[type[Provider]] = [
    Config,
    FrameworkService,
    Service
]
