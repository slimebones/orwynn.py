from orwynn.base.config import Config


class MongoConfig(Config):
    url: str
    database_name: str
