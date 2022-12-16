"""List of classes an user can subclass from."""
from orwynn.base.config.Config import Config
from orwynn.base.controller.controller import Controller
from orwynn.base.mapping.mapping import Mapping
from orwynn.base.middleware.middleware import Middleware
from orwynn.base.model.model import Model
from orwynn.base.service.service import Service


SUBCLASSABLE_CLASSES: list[type] = [
    Service,
    Controller,
    Middleware,
    Mapping,
    Model,
    Config
]
