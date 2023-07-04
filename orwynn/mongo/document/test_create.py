from orwynn.mongo.testing import Item


def test_create(mongo_boot):
    created = Item(name="pizza", price=1.2).create()

    assert created.name == "pizza"
    assert created.price == 1.2
