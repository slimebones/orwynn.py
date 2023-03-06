from orwynn.indication._Indication import Indication
from orwynn.indication._Indicator import Indicator


def test_default_indication_type():
    class E(Exception):
        pass

    i: Indication = Indication({
        "type": Indicator.TYPE,
        "value": Indicator.VALUE
    })

    assert i.digest(E("whatever"))["type"] == "error"
