from orwynn.module.Module import Module

from .Sql import Sql
from .SQLConfig import SQLConfig

module = Module(
    "/mongo",
    Providers=[Sql, SQLConfig],
    exports=[Sql, SQLConfig]
)
