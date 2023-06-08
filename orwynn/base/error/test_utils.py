
from orwynn.base.error.utils import (
    find_detailed_class_for_exception,
)


class Err1(Exception): pass
class Err1_1(Err1): pass
class Err2(Exception): pass


# NOTE: All passed exception lists are shuffled to ensure internal sorting is
#   performing right.


def test_builtin_exception():
    assert find_detailed_class_for_exception(
        ValueError("hello"),
        [Err1, Err2, ValueError, Exception]
    ) is ValueError
