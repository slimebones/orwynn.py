from enum import Enum

from orwynn.base.error.code import get_error_code
from orwynn.indication.indication import Indication
from orwynn.indication.indicator import Indicator
from orwynn.utils import validation


def test_int():
    class MyError(Exception):
        CODE = 1

    assert get_error_code(MyError()) == 1


def test_str():
    class MyError(Exception):
        CODE = "hello"

    assert get_error_code(MyError()) == "hello"


def test_enum():
    class ErrorCode(Enum):
        RED = "RED"

    class MyError(Exception):
        CODE = ErrorCode.RED

    assert get_error_code(MyError()) == ErrorCode.RED


def test_wrong_type():
    class MyError(Exception):
        CODE = 5.55

    validation.expect(
        get_error_code,
        validation.ValidationError,
        MyError()
    )


def test_no_attribute():
    class MyError(Exception):
        pass

    validation.expect(
        get_error_code,
        AttributeError,
        MyError()
    )

def test_default_indication_type():
    class E(Exception):
        pass

    i: Indication = Indication({
        "type": Indicator.TYPE,
        "value": Indicator.VALUE
    })

    assert i.digest(E("whatever"))["type"] == "error"
