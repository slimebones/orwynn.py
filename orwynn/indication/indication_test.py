from enum import Enum
from typing import Any

from pytest import fixture

from orwynn.indication.Indication import Indication
from orwynn.indication.Indicator import Indicator
from orwynn.model.Model import Model
from orwynn.parsing.parsing import parse_key
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

    assert mp_type == "Text"
    Text.parse_obj(mp_value)


def test_recover_default(default_indication: Indication):
    recovering_mp: dict[str, Any] = {
        "type": "Text",
        "value": {
            "text": "hello"
        }
    }

    recovered_model = default_indication.recover(recovering_mp)
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


def test_custom_model_api_type():
    class Item(Model):
        API_TYPE = "BestItem"
        name: str
        price: float

    i: Indication = Indication({
        "type": Indicator.TYPE,
        "value": Indicator.VALUE
    })

    assert i.digest(Item(name="pizza", price=2.3))["type"] == "BestItem"


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
