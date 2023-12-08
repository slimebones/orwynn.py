from enum import Enum
from typing import Any

from pykit import validation
from pytest import fixture

from orwynn.base.dto import ContainerDTO, UnitDTO
from orwynn.base.model.model import Model
from orwynn.indication.indication import Indication
from orwynn.indication.indicator import Indicator
from tests.std.text import Text


@fixture
def default_indication() -> Indication:
    mp: dict[str, Indicator] = {
        "type": Indicator.Type,
        "value": Indicator.Value
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
        "type": Indicator.Type,
        "value": Indicator.Value
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


def test_digest_polymorph(bare_boot):
    class ItemUDTO(UnitDTO):
        Code = "slimebones.orwynn.indication-testing.udto.item"
        price: float

    class SuperItemUDTO(ItemUDTO):
        Code = "slimebones.orwynn.indication-testing.udto.super-item"
        coolness: int

    class MiniItemUDTO(ItemUDTO):
        Code = "slimebones.orwynn.indication-testing.udto.mini-item"
        size: int

    class TinyItemUDTO(MiniItemUDTO):
        Code = "slimebones.orwynn.indication-testing.udto.tiny-item"
        is_really_small: bool

    class ItemCDTO(ContainerDTO):
        Base = ItemUDTO
        units: list[ItemUDTO]

    cdto = ItemCDTO(units=[
        ItemUDTO(id="1", price=10.5),
        SuperItemUDTO(id="2", price=50.3, coolness=100),
        MiniItemUDTO(id="3", price=2.1, size=3),
        TinyItemUDTO(id="4", price=1.5, size=1, is_really_small=True)
    ])

    api = cdto.api

    u = api["value"]["units"][0]
    assert u["id"] == "1"
    assert u["price"] == 10.5

    u = api["value"]["units"][1]
    assert u["id"] == "2"
    assert u["price"] == 50.3
    assert u["coolness"] == 100

    u = api["value"]["units"][2]
    assert u["id"] == "3"
    assert u["price"] == 2.1
    assert u["size"] == 3

    u = api["value"]["units"][3]
    assert u["id"] == "4"
    assert u["price"] == 1.5
    assert u["size"] == 1
    assert u["is_really_small"] is True
