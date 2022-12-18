from enum import Enum, auto


class UnitedConfigSourceType(Enum):
    """Reference to united source defined for all configs with this type at
    boottime."""
    UNITED_ENV = auto()
    UNITED_PATH = auto()
    UNITED_URI = auto()
