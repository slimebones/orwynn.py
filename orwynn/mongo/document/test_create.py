from orwynn.mongo.document.testing import SimpleDocument


def test_create(mongo_boot):
    created = SimpleDocument(name="pizza", price=1.2).create()

    assert created.name == "pizza"
    assert created.price == 1.2
