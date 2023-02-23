from enum import Enum


class Indicator(Enum):
    """List of indicators applicable to Schema's data representation.

    Values:
        TYPE:
            Indicates that field should contain any type representation of an
            object.
        VALUE:
            Indicates that field should contain a value of an object.
    """
    TYPE = "type"
    VALUE = "value"
