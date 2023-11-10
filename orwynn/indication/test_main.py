from enum import Enum
from typing import Any

from pytest import fixture

from orwynn.base.model.model import Model
from orwynn.indication.indication import Indication
from orwynn.indication.indicator import Indicator
from orwynn.utils import validation
from tests.std.text import Text


@fixture
def default_indication() -> Indication:
    mp: dict[str, Indicator] = {
        "type": Indicator.TYPE,
        "value": Indicator.VALUE
    }
    return Indication(mp)


def test_digest_default(default_indication: Indication):
    digested_mp: dict[str, Any] = default_indication.digest(
        Text(text="hello")
    )

    mp_type: str = validation.apply(digested_mp["type"], str)
    mp_value: dict = validation.apply(digested_mp["value"], dict)

    assert mp_type == "ok"
    Text.parse_obj(mp_value)


def test_recover_default(default_indication: Indication):
    recovering_mp: dict = {
        "type": "ok",
        "value": {
            "text": "hello"
        }
    }

    recovered_model: Text = default_indication.recover(Text, recovering_mp)
    assert type(recovered_model) is Text
    assert recovered_model.text == "hello"


def test_multiple_schemas():
    class Item(Model):
        name: str
        price: float

    i: Indication = Indication({
        "type": Indicator.TYPE,
        "value": Indicator.VALUE
    })

    assert i.gen_schema(Item) == i.gen_schema(Item)


def test_digest_enum(default_indication: Indication):
    class Color(Enum):
        RED = "red"
        GREEN = "green"

    class Priority(Enum):
        HIGH = 1
        LOW = 2

    class Item(Model):
        color: Color
        priority: Priority

        def __init__(self, **data: Any) -> None:
            super().__init__(**data)

    digested_mp: dict[str, Any] = default_indication.digest(
        Item(
            color="red",
            priority=1
        )
    )

    mp_value: dict = validation.apply(digested_mp["value"], dict)

    # Enum fields should be converted to values
    assert mp_value["color"] == "red"
    assert mp_value["priority"] == 1

    Item.parse_obj(mp_value)


def test_digest_error(default_indication: Indication):
    """
    Should digest error into API with external error code.
    """
    class ErrorCode(Enum):
        SIMPLE_CASE = "SIMPLE_CASE"
        ADVANCED_CASE = "ADVANCED_CASE"

    class SimpleError(Exception):
        Code = ErrorCode.SIMPLE_CASE

    class AdvancedError(Exception):
        Code = ErrorCode.ADVANCED_CASE

    class IntError(Exception):
        Code = 5

    class StrError(Exception):
        Code = "hello"

    data: dict

    data = default_indication.digest(SimpleError("hello world"))
    assert data["type"] == "error"
    assert data["value"]["message"] == "hello world"
    assert data["value"]["code"] == ErrorCode.SIMPLE_CASE.value

    data = default_indication.digest(AdvancedError("hello world"))
    assert data["type"] == "error"
    assert data["value"]["message"] == "hello world"
    assert data["value"]["code"] == ErrorCode.ADVANCED_CASE.value

    data = default_indication.digest(IntError("hello world"))
    assert data["type"] == "error"
    assert data["value"]["message"] == "hello world"
    assert data["value"]["code"] == 5

    data = default_indication.digest(StrError("hello world"))
    assert data["type"] == "error"
    assert data["value"]["message"] == "hello world"
    assert data["value"]["code"] == "hello"
