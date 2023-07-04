from orwynn.mongo.errors import DocumentUpdateError
from orwynn.mongo.testing import Item
from orwynn.utils import validation


def test_main(document_1: Item):
    assert document_1.update(set={"name": "beer"}).name == "beer"


def test_two_fields(document_1: Item):
    item: Item = document_1.update(set={"name": "beer", "price": 2.5})
    assert item.name == "beer"
    assert item.price == 2.5


def test_wrong_type(document_1: Item):
    validation.expect(
        document_1.update,
        DocumentUpdateError,
        set={"price": "sold out"}
    )


def test_unexistent(document_1: Item):
    validation.expect(
        document_1.update,
        DocumentUpdateError,
        set={"wow": "post malone"}
    )
