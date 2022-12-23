"""Scalable web-framework with out-of-the-box architecture."""
from orwynn import app, mongo, boot
# Bases are imported directly
from orwynn.base import (Config, Controller, Error, Indication, Indicator,
                         Model, Module, Mapping, Middleware)
from orwynn.util import validation, web
