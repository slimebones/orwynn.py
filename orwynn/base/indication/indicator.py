from enum import Enum


class Indicator(Enum):
    """List of indicators applicable to Schema's data representation.

    Values:
        Type:
            Indicates that field should contain any type representation of an
            object.
        Value:
            Indicates that field should contain a value of an object.
    """
    TYPE = 0
    VALUE = 1
