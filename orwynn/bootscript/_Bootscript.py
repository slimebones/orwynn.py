from orwynn.base.model import Model
from orwynn.bootscript._BootscriptCallable import BootscriptCallable
from orwynn.bootscript._CallTime import CallTime


class Bootscript(Model):
    fn: BootscriptCallable
    call_time: CallTime
