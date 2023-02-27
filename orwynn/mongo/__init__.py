from orwynn.base.module import Module
from ._Mongo import Mongo
from ._MongoConfig import MongoConfig
from ._Document import Document

module = Module(
    Providers=[Mongo, MongoConfig],
    exports=[Mongo, MongoConfig]
)
