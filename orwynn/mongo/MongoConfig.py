from orwynn.base.config.Config import Config
from orwynn.base.config.config_source.ConfigSource import ConfigSource
from orwynn.base.config.config_source.ConfigSourceType import ConfigSourceType

class MongoConfig(Config):
    uri: str = "mongodb://localhost:27017"
    database_name: str
