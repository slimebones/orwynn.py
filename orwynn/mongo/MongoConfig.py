from orwynn.base.config.Config import Config

class MongoConfig(Config):
    uri: str = "mongodb://localhost:27017"
    database_name: str
