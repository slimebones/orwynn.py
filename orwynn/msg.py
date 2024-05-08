"""
Some common messages.
"""
from pykit.fcode import code
from rxcat import Evt


@code("flag_evt")
class FlagEvt(Evt):
    val: bool

