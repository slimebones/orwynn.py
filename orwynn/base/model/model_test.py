from orwynn.base.model import Model


def test_random_id():
    class M1(Model):
        number: int

    m: Model = M1(number=1)

    assert m.id


def test_custom_id():
    class M1(Model):
        number: int

    m: Model = M1(id="helloworld", number=1)

    assert m.id == "helloworld"

