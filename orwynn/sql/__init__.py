from orwynn.module.Module import Module

from .Sql import Sql
from .SqlConfig import SqlConfig

module = Module(
    "/mongo",
    Providers=[Sql, SqlConfig],
    exports=[Sql, SqlConfig]
)
