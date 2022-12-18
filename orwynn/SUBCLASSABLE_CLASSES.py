"""List of classes an user can subclass from."""
from orwynn.base.config import Config
from orwynn.base.controller import Controller
from orwynn.base.mapping import Mapping
from orwynn.base.middleware import Middleware
from orwynn.base.model import Model
from orwynn.base.service import Service


SUBCLASSABLE_CLASSES: list[type] = [
    Service,
    Controller,
    Middleware,
    Mapping,
    Model,
    Config
]
