from orwynn.base.module.module import Module

from .config import SqlConfig
from .sql import Sql
from .table import Table

module = Module(
    Providers=[Sql, SqlConfig],
    exports=[Sql, SqlConfig]
)
