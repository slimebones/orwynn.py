"""
Scalable web-framework with out-of-the-box architecture.
"""

import importlib.metadata

from orwynn.config import Config
from orwynn.controller import Controller
from orwynn.database import Database
from orwynn.dto import (
    DTO,
    ContainerDTO,
    DTOUtils,
    UnitDTO,
    WebsocketCallDTO,
)
from orwynn.errorhandler import ErrorHandler
from orwynn.middleware import Middleware
from orwynn.model import Model
from orwynn.module import Module
from orwynn.service import Service
from orwynn.worker import Worker

__version__ = importlib.metadata.version("orwynn")

__all__ = [
    "Config",
    "Controller",
    "Database",
    "DTO",
    "ContainerDTO",
    "DTOUtils",
    "UnitDTO",
    "WebsocketCallDTO",
    "ErrorHandler",
    "Middleware",
    "Model",
    "Module",
    "Service",
    "Worker"
]
