from orwynn.mongo.testing import Item


def test_remove(document_1: Item, document_2: Item):
    assert document_1.remove() == document_1
    assert len(list(Item.find_all())) == 1
