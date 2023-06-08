from enum import Enum


class CallTime(Enum):
    """
    When a bootscript will be called.

    Options:
        AFTER_ALL:
            Bootscript will be launched after all framework's boot operations.
    """
    AFTER_ALL = "after_all"
