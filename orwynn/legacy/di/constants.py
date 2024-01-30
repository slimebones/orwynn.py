from orwynn.config import Config
from orwynn.controller.controller import Controller
from orwynn.di.acceptor import Acceptor
from orwynn.di.provider import Provider
from orwynn.errorhandler.errorhandler import ErrorHandler
from orwynn.middleware import Middleware
from orwynn.service import FrameworkService, Service

"""
List of builtin classes in Provider category.

Providers with higher priority cannot inject ones with lower priority.

This list: Lower index => higher priority.
"""
BUILTIN_PROVIDERS: list[type[Provider]] = [
    Config,
    FrameworkService,
    Service
]


"""
List of builtin classes are able to accept Providers.
"""
BUILTIN_ACCEPTORS: list[type[Acceptor]] = [
    # All Providers are Acceptors at the same time
    *BUILTIN_PROVIDERS,
    Controller,
    Middleware,
    ErrorHandler
]

