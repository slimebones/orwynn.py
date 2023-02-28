from orwynn.base.model._Model import Model
from orwynn.indication._Indication import Indication
from orwynn.indication._IndicationType import IndicationType
from orwynn.indication._Indicator import Indicator


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
