from orwynn.indication.Indication import Indication
from orwynn.indication.IndicationType import IndicationType
from orwynn.indication.Indicator import Indicator
from orwynn.model.Model import Model


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
