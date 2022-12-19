from orwynn.base.mapping.Mapping import Mapping
from orwynn.base.model.Model import Model


def test_custom_id():
    class M1(Mapping):
        number: int

    m: Mapping = M1(id="helloworld", number=1)

    assert m.id == "helloworld"
