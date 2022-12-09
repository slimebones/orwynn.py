from orwynn.src.base.controller.controller import Controller
from orwynn.src.base.middleware.middleware import Middleware
from orwynn.src.base.singleton.singleton import Singleton
from orwynn.src.di.BUILTIN_PROVIDERS import BUILTIN_PROVIDERS
from orwynn.src.util.types.acceptor import Acceptor


"""List of builtin classes are able to accept Providers.
"""
BUILTIN_ACCEPTORS: list[Acceptor] = [
    # All Providers are Acceptors at the same time
    *BUILTIN_PROVIDERS,
    Controller,
    Middleware
]