from enum import Enum
from typing import Any

from pytest import fixture

from orwynn.base.model._Model import Model
from orwynn.indication._Indication import Indication
from orwynn.indication._Indicator import Indicator
from orwynn.util.parsing import parse_key
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

    mp_type: str = parse_key("type", digested_mp, str)
    mp_value: dict = parse_key("value", digested_mp, dict)

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

    mp_value: dict = parse_key("value", digested_mp, dict)

    # Enum fields should be converted to values
    assert mp_value["color"] == "red"
    assert mp_value["priority"] == 1

    Item.parse_obj(mp_value)
