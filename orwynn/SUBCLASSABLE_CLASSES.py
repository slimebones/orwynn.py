"""List of classes an user can subclass from."""
from orwynn.base.controller.Controller import Controller
from orwynn.base.mapping.Mapping import Mapping
from orwynn.base.middleware._Middleware import Middleware
from orwynn.base.model.Model import Model
from orwynn.base.service.Service import Service


# Note that here listed the most basic classes. E.g. Config and ErrorHandler
# are not listed since they are derivatives from model and on the stage of DI
# it will be checked to find these more specific classes.
SUBCLASSABLE_CLASSES: list[type] = [
    Service,
    Controller,
    Middleware,
    Mapping,
    Model,
]
