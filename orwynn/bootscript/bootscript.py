from orwynn.base.model import Model
from orwynn.bootscript.callable import BootscriptCallable
from orwynn.bootscript.calltime import CallTime


class Bootscript(Model):
    fn: BootscriptCallable
    call_time: CallTime

    class Config:
        arbitrary_types_allowed = True
