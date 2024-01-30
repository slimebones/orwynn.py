from orwynn.bootscript.callable import BootscriptCallable
from orwynn.bootscript.calltime import CallTime
from orwynn.model import Model


class Bootscript(Model):
    func: BootscriptCallable
    call_time: CallTime

    class Config:
        arbitrary_types_allowed = True
