from orwynn.module.Module import Module
from orwynn.mongo.Mongo import Mongo
from orwynn.mongo.MongoConfig import MongoConfig

module = Module(
    "/mongo",
    Providers=[Mongo, MongoConfig],
    exports=[Mongo, MongoConfig]
)
