from orwynn.mongo.errors import DocumentUpdateError
from orwynn.mongo.testing import Item
from orwynn.utils import validation


def test_main(document_1: Item):
    item: Item = document_1.update(inc={"price": 2.5})
    assert item.price == 3.7


def test_wrong_type(document_1: Item):
    validation.expect(
        document_1.update,
        DocumentUpdateError,
        inc={"priority": 5.5}
    )


def test_unexistent(document_1: Item):
    validation.expect(
        document_1.update,
        DocumentUpdateError,
        inc={"wow": "post malone"}
    )
