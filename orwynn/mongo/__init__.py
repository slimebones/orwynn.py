from orwynn.base.module import Module

from ._Document import Document
from ._Mongo import Mongo
from ._MongoConfig import MongoConfig

module = Module(
    Providers=[Mongo, MongoConfig],
    exports=[Mongo, MongoConfig]
)
