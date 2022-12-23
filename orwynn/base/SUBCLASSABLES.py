"""List of classes an user can subclass from."""
from orwynn.base.controller.Controller import Controller
from orwynn.base.error.Error import Error
from orwynn.base.middleware.Middleware import Middleware
from orwynn.base.model.Model import Model
from orwynn.base.service.Service import Service
from orwynn.base.BaseSubclassable import BaseSubclassable


# Note that here listed the most basic classes. E.g. Config and ErrorHandler
# are not listed since they are derivatives from model and on the stage of DI
# it will be checked to find these more specific classes.
SUBCLASSABLES: list[BaseSubclassable] = [
    Service,
    Controller,
    Middleware,
    Model,
    Error
]
