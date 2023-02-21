from orwynn.src.module.Module import Module
from orwynn.src.mongo.Mongo import Mongo
from orwynn.src.mongo.MongoConfig import MongoConfig

module = Module(
    Providers=[Mongo, MongoConfig],
    exports=[Mongo, MongoConfig]
)
