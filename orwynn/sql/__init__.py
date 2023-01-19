from orwynn.module.Module import Module
from .SQL import SQL
from .SQLConfig import SQLConfig


module = Module(
    "/mongo",
    Providers=[SQL, SQLConfig],
)
