from .mapping import Mapping


def test_try_set_id():
    class M1(Mapping):
        number: int

    m: Mapping = M1(id="helloworld", number=1)

    assert m.id == "helloworld"
