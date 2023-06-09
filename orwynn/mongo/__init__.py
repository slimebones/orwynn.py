from orwynn.base.module import Module

from .document import Document
from .mongo import Mongo
from .config import MongoConfig

module = Module(
    Providers=[Mongo, MongoConfig],
    exports=[Mongo, MongoConfig]
)
