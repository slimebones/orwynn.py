"""
Some common messages.
"""
from rxcat import Evt


class FlagEvt(Evt):
    val: bool

