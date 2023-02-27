from orwynn.base.error import Error
from orwynn.base.error._find_detailed_class_for_exception import (
    find_detailed_class_for_exception,
)


class Err1(Error): pass
class Err1_1(Err1): pass
class Err2(Error): pass


# NOTE: All passed exception lists are shuffled to ensure internal sorting is
#   performing right.


def test_base_error():
    assert find_detailed_class_for_exception(
        Error("hello"),
        [Error, Exception]
    ) is Error


def test_custom_error():
    assert find_detailed_class_for_exception(
        Err1_1("hello"),
        [Error, ValueError, Exception, Err1]
    ) is Err1
    assert find_detailed_class_for_exception(
        Err1_1("hello"),
        [Exception, Error, Err1, Err1_1]
    ) is Err1_1
    assert find_detailed_class_for_exception(
        Err2("hello"),
        [Err1, Exception, Error, Err2]
    ) is Err2


def test_builtin_exception():
    assert find_detailed_class_for_exception(
        ValueError("hello"),
        [Error, Err1, Err2, ValueError, Exception]
    ) is ValueError
