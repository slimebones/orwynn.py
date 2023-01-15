
from orwynn import Config

from .SQLDatabase import SQLDatabase


class SQLConfig(Config):
    database_type: SQLDatabase
    database_name: str
    database_user: str | None = None
    database_password: str | None = None
    database_host: str | None = None
    database_port: int | None = None
