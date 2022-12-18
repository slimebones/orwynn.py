from enum import Enum, auto


class ConfigSourceType(Enum):
    ENV = auto()
    PATH = auto()
    URI = auto()
    _FWONLY = auto()
