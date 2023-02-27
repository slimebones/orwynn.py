from orwynn.base.module._Module import Module

from ._Sql import Sql
from ._SqlConfig import SqlConfig
from ._Table import Table

module = Module(
    Providers=[_Sql, _SqlConfig],
    exports=[_Sql, _SqlConfig]
)
