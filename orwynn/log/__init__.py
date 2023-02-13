from orwynn.log.Log import Log
from orwynn.log.LogConfig import LogConfig
from orwynn.module.Module import Module


module = Module(
    "/log",
    Providers=[Log, LogConfig],
    exports=[Log]
)
