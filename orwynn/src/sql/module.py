from orwynn.src.module.Module import Module

from .Sql import Sql
from .SqlConfig import SqlConfig

module = Module(
    Providers=[Sql, SqlConfig],
    exports=[Sql, SqlConfig]
)
