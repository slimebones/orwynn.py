from enum import Enum


class Validator(Enum):
    """Conventional object to represent cases requiring special validation.

    Values:
        SKIP:
            Don't care about type, just skip
    """
    SKIP = 0
