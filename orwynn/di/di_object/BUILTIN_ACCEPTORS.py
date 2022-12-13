from orwynn.base.controller.controller import Controller
from orwynn.base.middleware.middleware import Middleware
from orwynn.di.di_object.BUILTIN_PROVIDERS import BUILTIN_PROVIDERS
from orwynn.di.di_object.acceptor import Acceptor


"""List of builtin classes are able to accept Providers.
"""
BUILTIN_ACCEPTORS: list[type[Acceptor]] = [
    # All Providers are Acceptors at the same time
    *BUILTIN_PROVIDERS,
    Controller,
    Middleware
]
