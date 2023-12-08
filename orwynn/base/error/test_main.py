from enum import Enum

from pykit import validation

from orwynn.base.error.code import get_error_code
from orwynn.indication.indication import Indication
from orwynn.indication.indicator import Indicator


def test_int():
    class MyError(Exception):
        Code = 1

    assert get_error_code(MyError()) == 1


def test_str():
    class MyError(Exception):
        Code = "hello"

    assert get_error_code(MyError()) == "hello"


def test_enum():
    class ErrorCode(Enum):
        RED = "RED"

    class MyError(Exception):
        Code = ErrorCode.RED

    assert get_error_code(MyError()) == ErrorCode.RED


def test_wrong_type():
    class MyError(Exception):
        Code = 5.55

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
        "type": Indicator.Type,
        "value": Indicator.Value
    })

    assert i.digest(E("whatever"))["type"] == "error"
