from orwynn.base.module.module import Module

from ._Sql import Sql
from ._SqlConfig import SqlConfig
from ._Table import Table

module = Module(
    Providers=[Sql, SqlConfig],
    exports=[Sql, SqlConfig]
)
