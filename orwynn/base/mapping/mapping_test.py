from orwynn.base.mapping.Mapping import Mapping


def test_custom_id():
    class M1(Mapping):
        number: int

    m: Mapping = M1(id="helloworld", number=1)

    assert m.id == "helloworld"
