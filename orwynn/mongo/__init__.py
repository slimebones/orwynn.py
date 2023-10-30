from orwynn.base.module import Module
from orwynn.mongo.search import DocumentSearch, MongoStateFlagSearch
from orwynn.mongo.services import MongoStateFlagService
from orwynn.mongo.stateflag import MongoStateFlag
from orwynn.mongo.utils import MongoUtils

from .config import MongoConfig
from .document import Document
from .mongo import Mongo

__all__ = [
    "Document",
    "MongoConfig",
    "Mongo",
    "MongoUtils",
    "DocumentSearch",
    "MongoStateFlag",
    "MongoStateFlagSearch",
    "MongoStateFlagService"
]

module = Module(
    Providers=[Mongo, MongoConfig, MongoStateFlagService],
    exports=[Mongo, MongoConfig, MongoStateFlagService]
)
