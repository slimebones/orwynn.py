"""List of classes an user can subclass from."""
from orwynn.base.controller._Controller import Controller
from orwynn.base.error._Error import Error
from orwynn.base.mapping.Mapping import Mapping
from orwynn.base.middleware._Middleware import Middleware
from orwynn.base.model.Model import Model
from orwynn.base.service.Service import Service
from orwynn.base._BaseSubclassable import BaseSubclassable


# Note that here listed the most basic classes. E.g. Config and ErrorHandler
# are not listed since they are derivatives from model and on the stage of DI
# it will be checked to find these more specific classes.
SUBCLASSABLES: list[BaseSubclassable] = [
    Service,
    Controller,
    Middleware,
    Mapping,
    Model,
    Error
]
