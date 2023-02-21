from orwynn.src.indication.Indication import Indication
from orwynn.src.indication.IndicationType import IndicationType
from orwynn.src.indication.Indicator import Indicator
from orwynn.src.model.Model import Model


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
