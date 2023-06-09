from orwynn.base.module.module import Module

from .sql import Sql
from .config import SqlConfig
from .table import Table

module = Module(
    Providers=[Sql, SqlConfig],
    exports=[Sql, SqlConfig]
)
