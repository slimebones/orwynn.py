"""List of classes an user can subclass from."""
from orwynn.base.config.Config import Config
from orwynn.base.controller.Controller import Controller
from orwynn.base.mapping.Mapping import Mapping
from orwynn.base.middleware._Middleware import Middleware
from orwynn.base.model.Model import Model
from orwynn.base.service.Service import Service


SUBCLASSABLE_CLASSES: list[type] = [
    Service,
    Controller,
    Middleware,
    Mapping,
    Model,
    Config
]
