from typing import Any, Callable
from orwynn.base.model import Model

from orwynn.bootscript._CallTime import CallTime
from orwynn.bootscript._BootscriptCallable import BootscriptCallable


class Bootscript(Model):
    fn: BootscriptCallable
    call_time: CallTime
