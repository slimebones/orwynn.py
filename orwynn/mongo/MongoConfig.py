from orwynn.base.config import Config

class MongoConfig(Config):
    uri: str = "mongodb://localhost:27017"
    database_name: str
