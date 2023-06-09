from orwynn.base.model.model import Model
from orwynn.indication.indication import Indication
from orwynn.indication.indicator import Indicator
from orwynn.indication.type import IndicationType


def test_default_indication_type():
    class Item(Model):
        name: str
        price: float

    i: Indication = Indication({
        "type": Indicator.TYPE,
        "value": Indicator.VALUE
    })

    assert i.digest(Item(name="pizza", price=2.3))["type"] == "ok"


def test_custom_indication_type():
    class Item(Model):
        INDICATION_TYPE = IndicationType.ERROR
        name: str
        price: float

    i: Indication = Indication({
        "type": Indicator.TYPE,
        "value": Indicator.VALUE
    })

    assert i.digest(Item(name="pizza", price=2.3))["type"] == "error"
