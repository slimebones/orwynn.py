from orwynn.base.module import Module

from .config import MongoConfig
from .document import Document
from .mongo import Mongo

module = Module(
    Providers=[Mongo, MongoConfig],
    exports=[Mongo, MongoConfig]
)
