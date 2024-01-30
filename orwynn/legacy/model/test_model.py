from orwynn.indication.indication import Indication
from orwynn.indication.indicator import Indicator
from orwynn.indication.type import IndicationType
from orwynn.model.model import Model


def test_default_indication_type():
    class Item(Model):
        name: str
        price: float

    i: Indication = Indication({
        "type": Indicator.Type,
        "value": Indicator.Value
    })

    assert i.digest(Item(name="pizza", price=2.3))["type"] == "ok"


def test_custom_indication_type():
    class Item(Model):
        _IndicationType = IndicationType.Error
        name: str
        price: float

    i: Indication = Indication({
        "type": Indicator.Type,
        "value": Indicator.Value
    })

    assert i.digest(Item(name="pizza", price=2.3))["type"] == "error"
