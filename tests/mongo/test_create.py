from tests.mongo.conftest import SimpleDocument


def test_create():
    created = SimpleDocument(name="pizza", price=1.2).create()

    assert isinstance(created.sid, str)
    assert created.name == "pizza"
    assert created.price == 1.2
