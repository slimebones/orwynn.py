from typing import TypeVar

from orwynn.base.model import Model
from orwynn.sql import Table

TTable = TypeVar("TTable", bound=Table)
ConvertedModel = TypeVar("ConvertedModel", bound=Model)
# Contains many converted models
ListedConvertedModel = TypeVar("ListedConvertedModel", bound=Model)
