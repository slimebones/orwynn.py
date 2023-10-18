from orwynn.base.module import Module
from orwynn.mongo.search import DocumentSearch
from orwynn.mongo.utils import MongoUtils

from .config import MongoConfig
from .document import Document
from .mongo import Mongo

__all__ = [
    "Document",
    "MongoConfig",
    "Mongo",
    "MongoUtils",
    "DocumentSearch"
]

module = Module(
    Providers=[Mongo, MongoConfig],
    exports=[Mongo, MongoConfig]
)
